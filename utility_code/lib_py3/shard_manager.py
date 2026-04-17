import asyncio
import json
import logging
import re
from time import time
#from config import Config
import redis
from kubernetes import client as k8s_client

from lib_py3.lib_k8s import KubernetesManager
logger = logging.getLogger(__name__)
STATE_CACHE_TTL_SECONDS = 10
#config = Config()

class IllegalStatefulSetOperation(Exception):
    pass



class ShardManager(object):
    def __init__(self, namespace, redis_host="redis", redis_port=6379, shard_list=None):
        self._namespace = namespace
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._shards = set(shard_list) if shard_list else set()

        self._k8s = KubernetesManager(namespace)
        self._r = redis.Redis(host=self._redis_host, port=self._redis_port)
        # Get the list of shards from the config along with their types (deployment or statefulset) and store it in self._shards.
#        self._shards = config.get_shards(namespace)
        self.last_states = None
        self.last_update_time = None


    """ Redis schema:

    <namespace>:shardmanager:states  (hashmap)
        valley: {
            "type": "statefulset",
            "current_replicas": 3,
            "pods":{
                "valley-1": { # A statefulset member
                    "last_changed_timestamp": <integer unix timestamp in seconds>,
                    "last_state": <started>
                },
                "valley-2": { # A statefulset member
                    "last_changed_timestamp": <integer unix timestamp in seconds>,
                    "last_state": <stopped>
                }
            }
        },
        "blue-2": { # A deployment
            "type": "deployment",
            "current_replicas": 1,
            "pods":{
                "blue-2": { # A deployment member
                    "last_changed_timestamp": <integer unix timestamp in seconds>,
                    "last_state": <started>
                }
            }
        }

    <namespace>:shardmanager:scaling    (hashmap)
        valley: 3,
        blue-2: 1,
    """



    async def get_shard_states(self,force_refresh=False):
        """Common check for a shard's state for use in the summaries
        {
            "valley-2": {
                "type": "StatefulSet",
                "status": "starting",
                "last_change": <integer unix timestamp in seconds>,
            }
            "valley-2": {
                "type": "StatefulSet",
                "status": "starting",
                "last_change": <integer unix timestamp in seconds>,
            }
 }
        """
        if self.last_update_time is not None and not force_refresh and int(time()) - self.last_update_time > STATE_CACHE_TTL_SECONDS:
            return self.last_states

        # Call k8s.list() to get current state of each shard and its pods
        current_states = await self._k8s.list(self._shards)

        #print(f"current_states: {current_states}")

        # Make redis query to get desired scale for each deployment and statefulset. This will be used to determine if a shard is starting, stopping, or stable.
        desired_scaling_b = self._r.hgetall(f"{self._namespace}:shardmanager:scaling")
        desired_scaling = {}
        for shard_b, scale_b in desired_scaling_b.items():
            desired_scaling[shard_b.decode("utf-8")] = scale_b.decode("utf-8")
        print(f"desired_scaling:{desired_scaling}")

        # Add the desired scale to the current_states dict for each shard
        for shard, state in current_states.items():
            if shard in desired_scaling:
                state["desired_replicas"] = int(desired_scaling[shard])
            else:
                state["desired_replicas"] = state["current_replicas"] # If there is no desired scale in redis, assume the current scale is the desired scale

        #print(f"\ncurrent_states2: {current_states}")

        # Convert the current_states to the format of the redis schema
        converted_states = {}
        for shard, state in current_states.items():
            converted_states[shard] = {
                "type": state["type"],
                "current_replicas": state["current_replicas"],
                "desired_replicas": state["desired_replicas"],
                "pods": state["pods"]
            }
            if state["current_replicas"] < state["desired_replicas"]:
                # check all pods and add missing pods with a False
                for i in range(state["desired_replicas"]):
                    pod_name = f"{shard}-{i}" if state["type"] == "statefulset" else shard
                    if pod_name not in converted_states[shard]["pods"]:
                        converted_states[shard]["pods"][pod_name] = {"phase": "Stopped", "ready": False, "init": False}
            # add a field state to each pod based on the phase, init, and ready fields. If the pod is ready and initialized then state is started. If the pod is not ready and desired_replicas is 0 then state is stopped. If the pod is not ready and desired_replicas is 1 and previous state was stopped then state is starting. If the pod is not ready and desired_replicas is 1 and previous state was started then state is stopping.
            for pod_name, pod_info in converted_states[shard]["pods"].items():
                if pod_info["ready"] == True:
                    pod_info["state"] = "started"
                elif pod_info["ready"] == False and pod_info["phase"] == "Stopped":
                    pod_info["state"] = "stopped"
                elif pod_info["phase"] == "Running" and pod_info["init"] == True:
                    pod_info["state"] = "starting"
                elif pod_info["phase"] == "Terminating":
                    pod_info["state"] = "stopping"
                else:
                    # TODO: Edmund - Log some error here or throw an exception since this should not happen, but for now just set the state to unknown
                    pod_info["state"] = "UnknownState"

        # Get the previous state from redis
        previous_states_data = self._r.hgetall(f"{self._namespace}:shardmanager:states")
        previous_states = {}
        for shard_bytes, state_json_bytes in previous_states_data.items():
            previous_states[shard_bytes.decode("utf-8")] = json.loads(state_json_bytes.decode("utf-8"))

        # compare to the converted_states to determine if there are any changes
        update_shards = set()
        for shard, state in converted_states.items():
            if shard in previous_states:
                previous_state = previous_states[shard]
                # loop through the pods and check if any of them have changed state
                for pod_name, pod_info in state["pods"].items():
                    if pod_name in previous_state["pods"]:
                        previous_pod_info = previous_state["pods"][pod_name]
                        if "state" not in previous_pod_info:
                            previous_pod_info["state"] = "UnknownState"
                        if pod_info["state"] == previous_pod_info["state"]:
                            # If the state is the same, keep the previous last_change timestamp
                            if "last_change" in previous_pod_info:
                                pod_info["last_change"] = previous_pod_info["last_change"]
                            else:
                                pod_info["last_change"] = int(time())
                        else:
                            # Update the last_change timestamp for the pod if any pod has changed state
                            pod_info["last_change"] = int(time())
                            update_shards.add(shard)    
                    else:
                        # This is a new pod, set the last_change timestamp for the shard
                        pod_info["last_change"] = int(time())
                        update_shards.add(shard)
            else:
                # This is a new shard, set the last_change timestamp for all pods
                for pod_name, pod_info in state["pods"].items():
                    pod_info["last_change"] = int(time())
                    update_shards.add(shard)

        # Update the redis state with the updated states
        for shard, state in converted_states.items():
           if shard in update_shards:
            self._r.hset(f"{self._namespace}:shardmanager:states", shard, json.dumps(state))
        
        self.last_states = converted_states
        self.last_update_time = int(time())

        return converted_states


    async def start(self, shards: list):
        """
        Shard is either a deployment (old-style, ring-3) or a StatefulSet (valley) which has children.
        If a deployment then we can just scale it up to 1 replica. If a statefulset then we need to scale up the statefulset to the desired number of replicas set in redis
        Return an exception if a stateful set member is passed in
        """
        current_states = await(self.get_shard_states())
        # Validate all shards before starting any of them
        for shard in shards:
            if shard not in current_states.keys():
                if re.match(rf"^(.+)-\d+$", shard):
                    parent = re.match(rf"^(.+)-\d+$", shard).group(1)
                    if parent in current_states and current_states[parent]["type"] == "statefulset":
                        raise IllegalStatefulSetOperation(
                            f"Cannot start statefulset member '{shard}' directly. "
                            f"Use the parent statefulset name '{parent}' instead."
                        )
                raise Exception(f"Shard '{shard}' not found in namespace '{self._namespace}'")

        for shard in shards:
            shard_info = current_states[shard]

            if shard_info["type"] == "deployment":
                await self._k8s.start(shard)
                self._r.hset(f"{self._namespace}:shardmanager:scaling", shard, 1)

            elif shard_info["type"] == "statefulset":
                desired = self._r.hget(f"{self._namespace}:shardmanager:scaling", shard)
                if desired is None:
                    raise Exception(f"No desired replica count found in redis for statefulset '{shard}'")
                desired = int(desired)
                k8s_client.AppsV1Api().patch_namespaced_stateful_set(
                    shard, self._namespace, {"spec": {"replicas": desired}}
                )



    async def scale(self, shards: list, replicas: int):
        """
        Update the desired replica count for statefulsets and scale them immediately.
        Updates the redis scaling key so the new count persists across restarts.
        Raises IllegalStatefulSetOperation if a statefulset member is passed.
        Raises an exception if called on a deployment (deployments are always 0 or 1, use start/stop instead).
        """
        current_states = await(self.get_shard_states())

        # Validate all shards before scaling any of them
        for shard in shards:
            if shard not in current_states.keys():
                if re.match(rf"^(.+)-\d+$", shard):
                    parent = re.match(rf"^(.+)-\d+$", shard).group(1)
                    if parent in current_states and current_states[parent]["type"] == "statefulset":
                        raise IllegalStatefulSetOperation(
                            f"Cannot scale statefulset member '{shard}' directly. "
                            f"Use the parent statefulset name '{parent}' instead."
                        )
                raise Exception(f"Shard '{shard}' not found in namespace '{self._namespace}'")
            elif current_states[shard]["type"] == "deployment":
                raise Exception(f"Cannot scale deployment '{shard}'. Use start/stop instead.")

        for shard in shards:
            prev_desired = int(self._r.hget(f"{self._namespace}:shardmanager:scaling", shard))
            if prev_desired is None:
                prev_desired = current_states[shard]["current_replicas"]
            
            print(f"Scaling shard '{shard}' from {prev_desired} to {replicas} replicas")
            
            self._r.hset(f"{self._namespace}:shardmanager:scaling", shard, replicas)    
            k8s_client.AppsV1Api().patch_namespaced_stateful_set(
                shard, self._namespace, {"spec": {"replicas": replicas}}
            )

    async def stop(self, shards: list):
        """
        Shard is either a deployment or a StatefulSet.
        If a deployment then scale it down to 0 replicas.
        If a statefulset then scale it down to 0 replicas via k8s, but preserve the desired
        replica count in redis so that start() can restore it later.
        Raises IllegalStatefulSetOperation if a statefulset member is passed.
        """
        current_states = await(self.get_shard_states())

        # Validate all shards before starting any of them
        for shard in shards:
            if shard not in current_states.keys():
                if re.match(rf"^(.+)-\d+$", shard):
                    parent = re.match(rf"^(.+)-\d+$", shard).group(1)
                    if parent in current_states and current_states[parent]["type"] == "statefulset":
                        raise IllegalStatefulSetOperation(
                            f"Cannot stop statefulset member '{shard}' directly. "
                            f"Use the parent statefulset name '{parent}' instead."
                        )
                raise Exception(f"Shard '{shard}' not found in namespace '{self._namespace}'")

        for shard in shards:
            shard_info = current_states[shard]

            if shard_info["type"] == "deployment":
                await self._k8s.stop(shard)
                self._r.hset(f"{self._namespace}:shardmanager:scaling", shard, 0)

            elif shard_info["type"] == "statefulset":
                # Scale to 0 but leave the redis scaling key intact so start() can restore the count
                k8s_client.AppsV1Api().patch_namespaced_stateful_set(
                    shard, self._namespace, {"spec": {"replicas": 0}}
                )

    async def restart(self, shards: list):
        """
        Stop then start each shard. Delegates to stop() and start() so all validation
        and redis/k8s logic is handled consistently.
        """
        await self.stop(shards)
        await self.start(shards)

    @property
    def namespace(self):
        return self._namespace
