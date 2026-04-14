import asyncio
import redis

from lib_k8s import KubernetesManager


class IllegalStatefulSetOperation(Exception):
    pass



class ShardManager(object):
    def __init__(self, namespace, redis_host="redis", redis_port=6379):
        self._namespace = namespace
        self._redis_host = redis_host
        self._redis_port = redis_port

        self._k8s = KubernetesManager(namespace)
        self._r = redis.Redis(host=self._redis_host, port=self._redis_port)


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



    def get_shard_states(self):
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

        # Call k8s.list() to get current state
        # Make redis query to get desired state?

        pass

    def start(self, shards: list):
        """
        shard is either a deployment (old-style, ring-3) or a StatefulSet (valley) which has children.
        Return an exception if a stateful set member is passed in
        """
        pass

    def scale(self, shards):


    def stop(self, shards):
        pass

    def restart(self, shards):
        pass

    @property
    def namespace(self):
        return self._namespace
