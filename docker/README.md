# Building

```
docker build . -t monumenta-docker.injic.io/monumenta-java-shard --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000
docker build -t monumenta-docker.injic.io/monumenta-basic-ssh --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 --build-arg PASS=<thepassword> --file basic_ssh.Dockerfile .
```

# Logging in

```
docker login monumenta-docker.injic.io
```

# Push

```
docker push monumenta-docker.injic.io/monumenta-java-shard
docker push monumenta-docker.injic.io/monumenta-basic-ssh
```

# Kubernetes config:

```
kubectl create secret docker-registry regcred --docker-server=monumenta-docker.injic.io --docker-username=monumenta --docker-password=<password>
```



