#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

from pprint import pformat

from kubernetes import client, config

class KubernetesManager(object):
    def __init__(self):
        # TODO - specify via config
        self._namespace = "build-ns"

        # This only works within a pod - connects to the running k8s instance
        config.load_incluster_config()

    def _set_replicas(self, deployment_name, replicas):
        if replicas != 0 and replicas != 1:
            raise Exception("Replicas for {} must be either 0 or 1, not {}".format(name, replicas))
        try:
            client.AppsV1Api().patch_namespaced_deployment(deployment_name, "build-ns", {'spec': {'replicas': replicas}})
        except client.rest.ApiException as e:
            if e.status == 404:
                # Deployment does not exist
                raise Exception("{} not found".format(deployment_name))
            else:
                # Other error
                raise e

    def start(self, name):
        self._set_replicas("monumenta-{}-deployment".format(name), 1)

    def stop(self, name):
        self._set_replicas("monumenta-{}-deployment".format(name), 0)

    def restart(self, name):
        # TODO
        pass

    def list(self):
        result = {}

        # TODO: Filter by label so only actual shards are returned?
        query = client.AppsV1Api().list_namespaced_deployment(self._namespace)
        for deployment in query.items:
            name = deployment.metadata.name
            name = name.replace("monumenta-", "").replace("-deployment", "")

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
        #        if "monumenta-{}-deployment".format(deployment_name) in pod_name:
        #            result[deployment_name]["pod_name"] = pod_name
        #            break

        #for deployment_name in result:
        #    if "pod_name" in result[deployment_name]:
        #        logger.info(pformat(client.CoreV1Api().read_namespaced_pod_log(pod_name, self._namespace)))

        return result
