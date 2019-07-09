#!/usr/bin/env python3

from pprint import pprint

from kubernetes import client, config

class KubernetesManager(object):
    def __init__(self):
        # Define the barer token we are going to use to authenticate.
        # See here to create the token:
        # https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/
        token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkZWZhdWx0LXRva2VuLXpncWM5Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImRlZmF1bHQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIzY2I5M2NhZS02Mjc0LTRhZTQtYmUzOC00NzM0Zjg5YWIyZjYiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06ZGVmYXVsdCJ9.Vt6xQ-deIPgXmfa9x0xWMjo2D4bpgr8jwO3j4LbDqT3Rq2vZs0gnEBiLqFvWyc_Ybf4SloPHUt497HkhVRP7KJSAY6u4uFpJOwOB7j2inZ9L5hPleFQGbo9UpuQw6teRVD-FD39sPXeI-JE1OeUIKA5J0NsRufDsyQf7phiF7xmr9SvpRRIhdmTYNaWyM3kcFujmSO_olQJ06cUy_GoXCEdFVhkj6n6lW6BSM9mUYkcJYMrxsUZuBVZMchIkyqFFKewIvMkc57zyxKNsY4DIb3tpiz_DOsBbhOO_Tx09ta9x-JbuAgfZuCQvOJGdVVY3G8Dni9jusAjubJDkaVZ9zw"

        # Create a configuration object
        config = client.Configuration()

        # Specify the endpoint of your Kube cluster
        config.host = "https://192.168.1.90:16443"

        # Security part.
        # In this simple example we are not going to verify the SSL certificate of
        # the remote cluster (for simplicity reason)
        # Nevertheless if you want to do it you can with these 2 parameters
        # configuration.verify_ssl=True
        # ssl_ca_cert is the filepath to the file that contains the certificate.
        # configuration.ssl_ca_cert="certificate"
        # TODO
        config.verify_ssl = False

        config.api_key = {"authorization": "Bearer " + token}

        # Create a ApiClient with our config
        self._client = client
        self._api_client = client.ApiClient(config)

        self._namespace = "build-ns"

    def _set_replicas(self, deployment_name, replicas):
        if replicas != 0 and replicas != 1:
            raise Exception("Replicas for {} must be either 0 or 1, not {}".format(name, replicas))
        try:
            self._client.AppsV1Api(self._api_client).patch_namespaced_deployment(deployment_name, "build-ns", {'spec': {'replicas': replicas}})
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

        query = self._client.AppsV1Api(self._api_client).list_namespaced_deployment(self._namespace)
        for deployment in query.items:
            name = deployment.metadata.name
            name = name.replace("monumenta-", "").replace("-deployment", "")

            data = {}
            data["replicas"] = deployment.spec.replicas
            data["available_replicas"] = deployment.status.available_replicas
            result[name] = data

        query = self._client.CoreV1Api(self._api_client).list_namespaced_pod(self._namespace)
        for pod in query.items:
            pod_name = pod.metadata.name
            for deployment_name in result:
                if "monumenta-{}-deployment".format(deployment_name) in pod_name:
                    result[deployment_name]["pod_name"] = pod_name
                    break

        for deployment_name in result:
            if "pod_name" in result[deployment_name]:
                pprint(self._client.CoreV1Api(self._api_client).read_namespaced_pod_log(pod_name, self._namespace))

        #pprint(result)
        return result
