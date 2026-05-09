import asyncio
import datetime
import json
import logging
import re
from time import time
from datetime import datetime, timezone
import redis
from kubernetes import client as k8s_client

from lib_py3.lib_k8s import KubernetesManager
logger = logging.getLogger(__name__)
STATE_CACHE_TTL_SECONDS = 10
MAX_START_WAIT_SEC = 300  # 5 minutes
MAX_STOP_WAIT_SEC = 60    # 1 minute
START_POLL_INTERVAL_SECONDS = 5
STOP_POLL_INTERVAL_SECONDS = 2
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



    async def get_shard_states(self, force_refresh=False, shards=None):
        """Common check for a shard's state for use in the summaries
        {
            'ring-2': {
                'pods': {
                    'ring-2': {
                        'init': True, 'last_change': 1776293488,
                        'phase': 'Stopped', 'ready': False,
                        'state': 'stopped'}},
                'provisioned': 0, 'ready': 0, 'running': 0,
                'type': 'deployment'},
            'valley': {
                'pods': {
                    'valley-1': {
                        'init': False, 'last_change': 1777530260,
                        'phase': 'Stopped', 'ready': False,
                        'state': 'stopped'},
                    'valley-2': {
                        'init': True, 'last_change': 1777530260,
                        'phase': 'Running', 'ready': True,
                        'state': 'started'}},
                'provisioned': 2, 'ready': 0, 'running': 0,
                'type': 'statefulset'}
            }
        }
        """
        if self.last_update_time is not None and not force_refresh and int(time()) - self.last_update_time < STATE_CACHE_TTL_SECONDS:
            return self.last_states

        # Call k8s.list() to get current state of each shard and its pods
        current_states = await self._k8s.list(shards if shards is not None else self._shards)
        print(f"current_states: {current_states}")

        # Make redis query to get desired scale for each deployment and statefulset. This will be used to determine if a shard is starting, stopping, or stable.
        provisioned_b = self._r.hgetall(f"{self._namespace}:shardmanager:scaling")
        provisioned = {}
        for shard_b, scale_b in provisioned_b.items():
            provisioned[shard_b.decode("utf-8")] = scale_b.decode("utf-8")
        #print(f"provisioned:{provisioned}")

        # Add the desired scale to the current_states dict for each shard
        for shard, state in current_states.items():
            if shard in provisioned:
                state["provisioned"] = int(provisioned[shard])
            else:
                state["provisioned"] = state["running"] # If there is no desired scale in redis, assume the current scale is the desired scale

        #print(f"\ncurrent_states2: {current_states}")

        # Convert the current_states to the format of the redis schema
        converted_states = {}
        for shard, state in current_states.items():
            converted_states[shard] = {
                "type": state["type"],
                "running": state["running"],
                "provisioned": state["provisioned"],
                "ready": state["ready"],
                "pods": state["pods"]
            }
            if state["running"] < state["provisioned"]:
                # check all pods and add missing pods with a False
                for i in range(state["provisioned"]):
                    pod_name = f"{shard}-{i+1}" if state["type"] == "statefulset" else shard
                    if pod_name not in converted_states[shard]["pods"]:
                        converted_states[shard]["pods"][pod_name] = {"phase": "Stopped", "ready": False, "init": False}
            # add a field state to each pod based on the phase, init, and ready fields. If the pod is ready and initialized then state is started. If the pod is not ready and provisioned is 0 then state is stopped. If the pod is not ready and provisioned is 1 and previous state was stopped then state is starting. If the pod is not ready and provisioned is 1 and previous state was started then state is stopping.
            for pod_name, pod_info in converted_states[shard]["pods"].items():
                if pod_info["ready"] == True:
                    pod_info["state"] = "started"
                elif pod_info["ready"] == False and pod_info["phase"] == "Stopped":
                    pod_info["state"] = "stopped"
                elif pod_info["phase"] == "Running" and pod_info["init"] == True or pod_info["phase"] == "Pending":
                    pod_info["state"] = "starting"
                elif pod_info["phase"] == "Terminating":
                    pod_info["state"] = "stopping"
                else:
                    # TODO: Log some error here or throw an exception since this should not happen, but for now just set the state to unknown
                    pod_info["state"] = "UnknownState"

        # Get the previous state from redis
        previous_states_data = self._r.hgetall(f"{self._namespace}:shardmanager:states")
        previous_states = {}
        for shard_bytes, state_json_bytes in previous_states_data.items():
            previous_states[shard_bytes.decode("utf-8")] = json.loads(state_json_bytes.decode("utf-8"))

        # compare to the converted_states to determine if there are any changes
        update_shards = set()
        tz = timezone.utc
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
                                pod_info["last_change"] = int(datetime.now(tz).timestamp())
                        else:
                            # Update the last_change timestamp for the pod if any pod has changed state
                            pod_info["last_change"] = int(datetime.now(tz).timestamp())
                            update_shards.add(shard)    
                    else:
                        # This is a new pod, set the last_change timestamp for the shard
                        pod_info["last_change"] = int(datetime.now(tz).timestamp())
                        update_shards.add(shard)
            else:
                # This is a new shard, set the last_change timestamp for all pods
                for pod_name, pod_info in state["pods"].items():
                    pod_info["last_change"] = int(datetime.now(tz).timestamp())
                    update_shards.add(shard)

        # Update the redis state with the updated states
        for shard, state in converted_states.items():
            if shard in update_shards:
                self._r.hset(f"{self._namespace}:shardmanager:states", shard, json.dumps(state))
        
        self.last_states = converted_states
        self.last_update_time = int(datetime.now(tz).timestamp())

        return converted_states


    async def start(self, shards: list, wait: bool = True, timeout_seconds=MAX_START_WAIT_SEC):
        """
        Shard is either a deployment (with only 1 replica) or a StatefulSet (with one or more replicas).
        If a deployment then we can just scale it up to 1 replica. If a statefulset then we need to scale 
        up the statefulset to the provisioned number of replicas stored in redis.
        Return an exception if a stateful set member is passed in
        """
        if not isinstance(shards, list):
            shards = [shards]
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
                provisioned = self._r.hget(f"{self._namespace}:shardmanager:scaling", shard)
                if provisioned is None:
                    raise Exception(f"No provisioned replica count found in redis for statefulset '{shard}'")
                provisioned = int(provisioned)
                
                await self._k8s._set_statefulset_replicas({shard: provisioned})
        
        if wait:
            deadline = time() + timeout_seconds
            while True:
                print(f"Waiting for shards {shards} to start...")
                states = await self.get_shard_states(force_refresh=True, shards=shards)
                def _started(shard):
                    info = states[shard]
                    if info["type"] == "deployment":
                        return info["ready"] == 1
                    desired = int(self._r.hget(f"{self._namespace}:shardmanager:scaling", shard) or 0)
                    return info["ready"] == desired
                if all(_started(shard) for shard in shards):
                    break
                if time() >= deadline:
                    raise TimeoutError(f"Shards {shards} did not start within {MAX_START_WAIT_SEC}s")
                await asyncio.sleep(START_POLL_INTERVAL_SECONDS)


    async def scale(self, shards: list, new_scale: int, wait: bool = True, timeout_seconds=MAX_START_WAIT_SEC):
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

        scaling_up = {}
        for shard in shards:
            prev_provisioned = self._r.hget(f"{self._namespace}:shardmanager:scaling", shard)
            if prev_provisioned is not None and int(prev_provisioned) == new_scale and current_states[shard]["running"] == new_scale:
                print(f"Shard '{shard}' is already scaled to {new_scale}")
                continue
            else:
                print(f"Setting Shard '{shard}' provisioned replicas to {new_scale}")
                self._r.hset(f"{self._namespace}:shardmanager:scaling", shard, new_scale)

            if new_scale == current_states[shard]["running"]:
                print(f"Shard '{shard}' is already scaled to {new_scale}")
                continue
            
            scaling_up[shard] = new_scale > current_states[shard]["running"]
            print(f"Scaling shard '{shard}' from {current_states[shard]['running']} to {new_scale} replicas")

            await self._k8s._set_statefulset_replicas({shard: new_scale})

        if wait and scaling_up:
            deadline = time() + timeout_seconds
            shards_wait = list(scaling_up.keys())
            while True:
                print(f"Waiting for shards {shards_wait} to scale to {new_scale} replicas...")
                states = await self.get_shard_states(force_refresh=True, shards=shards_wait)
                def _done(shard):
                    field = "ready" if scaling_up[shard] else "running"
                    return states[shard][field] == new_scale
                if all(_done(shard) for shard in shards_wait):
                    break
                if time() >= deadline:
                    raise TimeoutError(f"Shards {shards_wait} did not scale to {new_scale} replicas within {MAX_START_WAIT_SEC}s")
                await asyncio.sleep(START_POLL_INTERVAL_SECONDS)

    async def stop(self, shards: list, wait: bool = True, timeout_seconds=MAX_STOP_WAIT_SEC):
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
            if current_states[shard]["running"] == 0:
                print(f"Shard '{shard}' is already stopped")
                continue

            if shard_info["type"] == "deployment":
                await self._k8s.stop(shard, type="deployment")
                

            elif shard_info["type"] == "statefulset":
                # Scale to 0 but leave the redis scaling key intact so start() can restore the count
                await self._k8s.stop(shard, type="statefulset")

        if wait:
            deadline = time() + timeout_seconds
            while True:
                states = await self.get_shard_states(force_refresh=True, shards=shards)
                if all(states[shard]["running"] == 0 for shard in shards):
                    break
                if time() >= deadline:
                    raise TimeoutError(f"Shards {shards} did not stop within {MAX_STOP_WAIT_SEC}s")
                await asyncio.sleep(STOP_POLL_INTERVAL_SECONDS)

    async def restart(self, shards: list, wait: bool = True, timeout_seconds=MAX_START_WAIT_SEC):
        """
        Restart each shard.
        - Deployments that are running: delete their pod so the deployment controller recreates it.
        - Deployments that are stopped: start them.
        - Statefulset pods (e.g. "valley-1") that are running: delete the pod so k8s recreates it.
        - Statefulset parents (e.g. "valley"): stop then start.
        """
        current_states = await self.get_shard_states()

        to_stop = []
        to_start = []
        pod_deletes = []

        for shard in shards:
            if shard in current_states:
                shard_info = current_states[shard]
                if shard_info["type"] == "deployment":
                    running_pods = [p for p, info in shard_info["pods"].items()
                                    if info.get("phase") not in ("Stopped", "Terminating")]
                    if running_pods:
                        to_stop.append(shard)
                    else:
                        to_start.append(shard)
                    continue
                elif shard_info["type"] == "statefulset":
                    if shard_info["running"] > 0:
                        to_stop.append(shard)
                    else:
                        to_start.append(shard)
                    continue
            # Check if it's an individual statefulset pod (e.g. "valley-1")
            match = re.match(rf"^(.+)-(\d+)$", shard)
            if match:
                parent = match.group(1)
                if parent in current_states and current_states[parent]["type"] == "statefulset":
                    pods = current_states[parent]["pods"]
                    if shard in pods:
                        if pods[shard].get("phase") not in ("Stopped", "Terminating"):
                            pod_deletes.append(shard)
                        to_start.append(parent)
                        continue
            raise IllegalStatefulSetOperation(f"Shard '{shard}' not found in namespace '{self._namespace}'")

        for pod_name in pod_deletes:
            # This will cause the statefulset controller to recreate the pod with the same name. It's a clean way to restart a pod in a statefulset.
            # If it's a pod in a stateful set, then it will come back up with the same name and ordinal. 
            await self._k8s.delete_pod(pod_name)

        if to_stop:
            await self.stop(to_stop, wait=False)
        
        if to_start:
            await self.start(to_start, wait=False)
        
        if wait:
            deadline = time() + timeout_seconds
            while True:
                
                if to_stop:                    
                    states = await self.get_shard_states(force_refresh=True, shards=to_stop)
                    rm = []
                    for shard in to_stop:
                        if states[shard]["running"] == 0:
                            print(f"Shard '{shard}' has stopped, restarting now")
                            await self.start(shard, wait=False)
                            to_start.append(shard)
                            rm.append(shard)
                    for shard in rm:
                        to_stop.remove(shard)
                
                if to_start:
                    states = await self.get_shard_states(force_refresh=True, shards=to_start)
                    rm = []
                    for shard in to_start:
                        info = states[shard]
                        if info["type"] == "deployment" and info["ready"] == 1:
                            print(f"Shard '{shard}' has completed restart")
                            rm.append(shard)
                        elif info["type"] == "statefulset" and info["ready"] == info["provisioned"] and info["provisioned"] != 0:
                            print(f"Shard '{shard}' of type statefulset has completed restart")
                            rm.append(shard)
                    for shard in rm:
                        to_start.remove(shard)
                if not to_stop and not to_start:
                    break
                if time() >= deadline:
                    raise TimeoutError(f"Shards {shards} did not restart within {MAX_START_WAIT_SEC}s")
                await asyncio.sleep(START_POLL_INTERVAL_SECONDS)

    @property
    def namespace(self):
        return self._namespace
