#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

from pprint import pformat

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

    def _set_replicas(self, deployment_name, replicas):
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

    def start(self, name):
        self._set_replicas(name.replace('_', ''), 1)

    def stop(self, name):
        self._set_replicas(name.replace('_', ''), 0)

    def restart(self, name):
        # TODO
        pass

    def list(self):
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
