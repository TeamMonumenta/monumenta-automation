#!/usr/bin/env python3

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
                raise Exception("Replicas for {} must be either 0 or 1, not {}".format(name, replicas))
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
            # TODO Better wait! - on stop needs to wait for terminated pod, on start needs to wait for readiness
            await asyncio.sleep(15)

    async def _start_stop_common(self, names, replicas, wait, timeout_seconds):
        deployment_map = {}
        if type(names) is list:
            for name in names:
                deployment_map[name] = replicas
        else:
            deployment_map[names] = replicas
        await self._set_replicas(deployment_map, wait, timeout_seconds)

    async def start(self, names, wait=True, timeout_seconds=60):
        await self._start_stop_common(names, 1, wait, timeout_seconds)

    async def stop(self, names, wait=True, timeout_seconds=60):
        await self._start_stop_common(names, 0, wait, timeout_seconds)

    async def restart(self, names, wait=True, timeout_seconds=60):
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

        logger.debug("Deployment list: {}".format(pformat(result)))

        # TODO: Use this elsewhere?
        #query = client.CoreV1Api().list_namespaced_pod(self._namespace)
        #for pod in query.items:
        #    pod_name = pod.metadata.name
        #    for deployment_name in result:
        #        if deployment_name in pod_name:
        #            result[deployment_name]["pod_name"] = pod_name
        #            break

        #for deployment_name in result:
        #    if "pod_name" in result[deployment_name]:
        #        logger.info(pformat(client.CoreV1Api().read_namespaced_pod_log(pod_name, self._namespace)))

        return result
