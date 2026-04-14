import asyncio
import re
from pprint import pformat

import logging
logger = logging.getLogger(__name__)

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

    async def _set_replicas(self, deployment_map, wait, timeout_seconds):
        # deployment_map = { deployment_name (string) : replicas (int) }
        # ex: { "bungee" : 1 }

        for deployment_name in deployment_map:
            replicas = deployment_map[deployment_name]
            if replicas != 0 and replicas != 1:
                raise Exception(f"Replicas for {name} must be either 0 or 1, not {replicas}")
            try:
                client.AppsV1Api().patch_namespaced_deployment(deployment_name, self._namespace, {'spec': {'replicas': replicas}})
            except client.rest.ApiException as e:
                if e.status == 404:
                    # Deployment does not exist
                    raise Exception("{} not found".format(deployment_name))
                else:
                    # Other error
                    raise e

        if wait:
            sleep_count = 0
            while True:
                shards = await self.list()

                all_done = True
                for shard in deployment_map:
                    if deployment_map[shard] == 0:
                        # Stopping - check for still alive pods
                        if "pod_name" in shards[shard]:
                            all_done = False
                    else:
                        # Starting - check available replicas
                        if shards[shard]['available_replicas'] != 1:
                            all_done = False

                if all_done:
                    break

                if sleep_count >= timeout_seconds:
                    raise Exception(f"Exceeded {timeout_seconds}s waiting for shards to start or stop")
                sleep_count += 1
                await asyncio.sleep(1)


    async def _start_stop_common(self, names, replicas, wait, timeout_seconds):
        deployment_map = {}
        if type(names) is not list:
            names = [names,]
        for name in names:
            deployment_map[name.replace("_", "")] = replicas

        await self._set_replicas(deployment_map, wait, timeout_seconds)

    async def start(self, names, wait=True, timeout_seconds=240):
        await self._start_stop_common(names, 1, wait, timeout_seconds)

    async def stop(self, names, wait=True, timeout_seconds=90):
        await self._start_stop_common(names, 0, wait, timeout_seconds)

    async def restart(self, names, wait=True, timeout_seconds=240):
        await self.stop(names, wait, timeout_seconds)
        await self.start(names, wait, timeout_seconds)

    async def list(self):
        '''
        Returns a list of all the pods from all the deployments and statefulsets in the following format:
        {'tutorial': {'available_replicas': 0,
            'label_selector': 'app=tutorial',
            'pods': [],
            'replicas': 0,
            'type': 'deployment'},
         'valley': {'available_replicas': 1,
            'label_selector': 'app=valley',
            'pods': [('valley-1', True), ('valley-2', False)],
            'replicas': 2,
            'type': 'statefulset'},
         'velocity-17': {'available_replicas': 1,
            'label_selector': 'app=velocity-17',
            'pods': [('velocity-17-5f695c955c-r5hgz', True)],
            'replicas': 1,
            'type': 'deployment'}}
        '''
        result = {}

        # TODO: Filter by label so only actual shards are returned?
        query = client.AppsV1Api().list_namespaced_deployment(self._namespace)
        
        for deployment in query.items:
            name = deployment.metadata.name

            data = {}
            data["type"] = "deployment"
            data["replicas"] = deployment.spec.replicas
            if deployment.status.available_replicas is None:
                data["available_replicas"] = 0
            else:
                data["available_replicas"] = deployment.status.available_replicas
            #labels = deployment.spec.selector.match_labels
            #data["label_selector"] = ",".join([f"{k}={v}" for k, v in labels.items()])
            #data["pods"] = []
            result[name] = data

        query = client.AppsV1Api().list_namespaced_stateful_set(self._namespace)
        for statefulset in query.items:
            name = statefulset.metadata.name

            data = {}
            data["type"] = "statefulset"
            data["replicas"] = statefulset.spec.replicas
            if statefulset.status.available_replicas is None:
                data["available_replicas"] = 0
            else:
                data["available_replicas"] = statefulset.status.available_replicas
            
            # TODO: Edmund - We need to now this number so that we can display the correct number of pods
            # that are offline.
            data["total_replicas"] = "<replace this with the desired/max number of replicas stored in redis>"
            
            labels = statefulset.spec.selector.match_labels
            data["label_selector"] = ",".join([f"{k}={v}" for k, v in labels.items()])
            data["pods"] = []
            result[name] = data

        for item in result:
            if "label_selector" not in result[item].keys():
                continue
            label_selector = result[item]["label_selector"]
            pods = client.CoreV1Api().list_namespaced_pod(namespace=self._namespace,label_selector=label_selector)
            
            for pod in pods.items:
                pod_name = pod.metadata.name
                pod_ready = False
                pod_details = client.CoreV1Api().read_namespaced_pod(name=pod_name, namespace=self._namespace)
                for condition in pod_details.status.conditions:
                    if condition.type == 'Ready':
                        pod_ready = condition.status == 'True'
                result[item]["pods"].append((pod_name, pod_ready))

        logger.debug("Deployment list: {}".format(pformat(result)))

        #for deployment_name in result:
        #    if "pod_name" in result[deployment_name]:
        #        logger.info(pformat(client.CoreV1Api().read_namespaced_pod_log(pod_name, self._namespace)))

        return result

    @property
    def namespace(self):
        return self._namespace
