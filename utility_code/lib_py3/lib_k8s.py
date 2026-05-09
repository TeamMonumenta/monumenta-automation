import asyncio
import re
from pprint import pformat

import logging
import urllib3
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from kubernetes import client, config

class KubernetesManager(object):
    def __init__(self, namespace):
        self._namespace = namespace

        try:
            # This only works within a pod - connects to the running k8s instance
            config.load_incluster_config()
        except config.config_exception.ConfigException as e:
            try:
                # If loading incluster_config failed, try to load regular config file from user's ~/.kube
                config.load_kube_config()
            except config.config_exception.ConfigException as e:
                raise Exception("Failed to load k8s config - is the environment set up?")

        # Disable SSL verification on the loaded config (needed when connecting via SSH tunnel)
        conf = client.Configuration.get_default_copy()
        conf.verify_ssl = False
        client.Configuration.set_default(conf)

    async def _set_deployment_replicas(self, deployment_map):
        # deployment_map = { deployment_name (string) : replicas (int) }
        # ex: { "bungee" : 1 }

        for deployment_name in deployment_map:
            replicas = deployment_map[deployment_name]
            if replicas != 0 and replicas != 1:
                raise Exception(f"Replicas for {deployment_name} must be either 0 or 1, not {replicas}")
            try:
                client.AppsV1Api().patch_namespaced_deployment(deployment_name, self._namespace, {'spec': {'replicas': replicas}})
            except client.rest.ApiException as e:
                if e.status == 404:
                    # Deployment does not exist
                    raise Exception("{} not found".format(deployment_name))
                else:
                    # Other error
                    raise e
    
    async def _set_statefulset_replicas(self, statefulset_map):
        # statefulset_map = { statefulset_name (string) : replicas (int) }
        # ex: { "bungee" : 1 }

        for statefulset_name in statefulset_map:
            replicas = statefulset_map[statefulset_name]
            try:
                client.AppsV1Api().patch_namespaced_stateful_set(statefulset_name, self._namespace, {'spec': {'replicas': replicas}})
            except client.rest.ApiException as e:
                if e.status == 404:
                    # StatefulSet does not exist
                    raise Exception("{} not found".format(statefulset_name))
                else:
                    # Other error
                    raise e


    async def _start_stop_deployment_common(self, names, replicas, timeout_seconds):
        deployment_map = {}
        if type(names) is not list:
            names = [names,]
        for name in names:
            deployment_map[name.replace("_", "")] = replicas

        await self._set_deployment_replicas(deployment_map)

    async def _start_stop_statefulset_common(self, names, replicas):
        statefulset_map = {}
        if type(names) is not list:
            names = [names,]
        for name in names:
            statefulset_map[name.replace("_", "")] = replicas

        await self._set_statefulset_replicas(statefulset_map)


    async def start(self, names, wait=True, type="deployment", replicas=1):
        if type == "deployment":
            await self._start_stop_deployment_common(names, replicas, wait)
        elif type == "statefulset":
            await self._start_stop_statefulset_common(names, replicas, wait)

    async def stop(self, names, wait=True, timeout_seconds=90, type="deployment"):
        if type == "deployment":
            await self._start_stop_deployment_common(names, 0, timeout_seconds)
        elif type == "statefulset":
            await self._start_stop_statefulset_common(names, 0)

    async def delete_pod(self, pod_name):
        try:
            client.CoreV1Api().delete_namespaced_pod(pod_name, self._namespace)    
        except client.rest.ApiException as e:
            if e.status == 404:
                # Pod does not exist
                raise Exception("{} not found".format(pod_name))
            else:
                # Other error
                raise e

    async def list(self, shards=None):
        '''
        Returns a list of all the pods from all the deployments and statefulsets in the following format:
        {
            "ring-2": {
                "type": "deployment", "running": 0, "ready": 0, "label_selector": "app=ring-2", 
                "pods": {
                    "ring-2": {
                        "phase": "Stopped", "ready": False, "init": True
                    }
                }
            }, "valley": {
                "type": "statefulset", "running": 0, "ready": 0, "label_selector": "app=valley", 
                "pods": {
                    "valley-1": {
                        "phase": "Running", "ready": False, "init": True
                    }, "valley-2": {
                        "phase": "Running", "ready": True, "init": True}
                    }
            }
        }
        '''
        result = {}
        shards_set = set(shards) if shards is not None else None
                
        # TODO: Filter by label so only actual shards are returned?
        query = client.AppsV1Api().list_namespaced_deployment(self._namespace)
        
        for deployment in query.items:
            name = deployment.metadata.name
            if shards is not None and name not in shards:
                continue
            data = {}
            data["type"] = "deployment"
            data["running"] = deployment.spec.replicas
            if deployment.status.available_replicas is None:
                data["ready"] = 0
            else:
                data["ready"] = deployment.status.available_replicas
            labels = deployment.spec.selector.match_labels
            data["label_selector"] = ",".join([f"{k}={v}" for k, v in labels.items()])
            data["pods"] = {}
            result[name] = data

        query = client.AppsV1Api().list_namespaced_stateful_set(self._namespace)
        for statefulset in query.items:
            name = statefulset.metadata.name
            if shards is not None and name not in shards:
                continue
            data = {}
            data["type"] = "statefulset"
            data["running"] = statefulset.spec.replicas
            if statefulset.status.available_replicas is None:
                data["ready"] = 0
            else:
                data["ready"] = statefulset.status.available_replicas
            
            labels = statefulset.spec.selector.match_labels
            data["label_selector"] = ",".join([f"{k}={v}" for k, v in labels.items()])
            data["pods"] = {}
            result[name] = data

        for item in result:
            if result[item]["type"] == "deployment":
                # For speed, derive the phase and readiness of the pod based on the values from the deployemnt.
                # Unfortunately the deployment object doesn't give us the phase of the pod so we can't know if it's terminating.
                # We can infer the other three states: stopped, starting, and started.
                running = "Running" if result[item]["running"] == 1 else "Stopped"
                pod_ready = result[item]["ready"] == 1
                result[item]["pods"][item] = {"phase":running, "ready":pod_ready, "init":True}
                
            elif result[item]["type"] == "statefulset" and "label_selector" in result[item].keys():
                all_pods_stopped = result[item]["running"] == 0
                all_pods_ready = result[item]["ready"] == result[item]["running"]
                if all_pods_stopped or all_pods_ready:
                    # If all pods are stopped or all pods are ready, we can infer the phase and readiness of the pods without making individual API calls.
                    phase = "Stopped" if all_pods_stopped else "Running"
                    for i in range(result[item]["running"]):
                        pod_name = f"{item}-{i+1}"
                        result[item]["pods"][pod_name] = {"phase":phase, "ready":all_pods_ready, "init":True}
                    continue
                label_selector = result[item]["label_selector"]
                pods = client.CoreV1Api().list_namespaced_pod(namespace=self._namespace,label_selector=label_selector)
                
                for pod in pods.items:
                    pod_name = pod.metadata.name
                    
                    pod_ready = False
                    initialized = False
                    try:
                        pod_details = client.CoreV1Api().read_namespaced_pod(name=pod_name, namespace=self._namespace)
                    except Exception as e:
                        print("Error occurred while fetching pod details for {}: {}".format(pod_name, str(e)))
                        logger.error("Error occurred while fetching pod details for {}: {}".format(pod_name, str(e)))
                        continue
                    for condition in pod_details.status.conditions:
                        if condition.type == 'Ready':
                            pod_ready = condition.status == 'True'
                        if condition.type == 'Initialized':
                            initialized = condition.status == 'True'
                    result[item]["pods"][pod_name] = {"phase":pod_details.status.phase, "ready":pod_ready, "init":initialized}

        logger.debug("Deployment list: {}".format(pformat(result)))

        #for deployment_name in result:
        #    if "pod_name" in result[deployment_name]:
        #        logger.info(pformat(client.CoreV1Api().read_namespaced_pod_log(pod_name, self._namespace)))

        return result

    @property
    def namespace(self):
        return self._namespace
