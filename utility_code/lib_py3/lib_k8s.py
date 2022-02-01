import asyncio
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
        result = {}

        # TODO: Filter by label so only actual shards are returned?
        query = client.AppsV1Api().list_namespaced_deployment(self._namespace)
        for deployment in query.items:
            name = deployment.metadata.name

            data = {}
            data["replicas"] = deployment.spec.replicas
            if deployment.status.available_replicas is None:
                data["available_replicas"] = 0
            else:
                data["available_replicas"] = deployment.status.available_replicas
            result[name] = data

        query = client.CoreV1Api().list_namespaced_pod(self._namespace)
        for pod in query.items:

            pod_name = pod.metadata.name
            for deployment_name in result:
                if pod_name.startswith(deployment_name):
                    result[deployment_name]["pod_name"] = pod_name
                    break

        logger.debug("Deployment list: {}".format(pformat(result)))

        #for deployment_name in result:
        #    if "pod_name" in result[deployment_name]:
        #        logger.info(pformat(client.CoreV1Api().read_namespaced_pod_log(pod_name, self._namespace)))

        return result

    @property
    def namespace(self):
        return self._namespace
