# Building

```
docker build . -t monumenta-docker.injic.io/monumenta-java-shard --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000
```

# Logging in

```
docker login monumenta-docker.injic.io
```

# Push

```
docker push monumenta-docker.injic.io/monumenta-java-shard
```

# Kubernetes config:

```
kubectl create secret docker-registry regcred --docker-server=monumenta-docker.injic.io --docker-username=monumenta --docker-password=<password>
```



