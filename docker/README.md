# Building

```
docker build . --file java-shard.Dockerfile -t monumenta-docker.injic.io/monumenta-java-shard --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000
docker build . --file basic_ssh.Dockerfile -t monumenta-docker.injic.io/monumenta-basic-ssh --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 --build-arg PASS=<thepassword>
docker build .. --file automation-bot.Dockerfile -t monumenta-docker.injic.io/monumenta-automation-bot --build-arg USERNAME=rock --build-arg UID=1000 --build-arg GID=1000
```

# Logging in

```
docker login monumenta-docker.injic.io
```

# Push

```
docker push monumenta-docker.injic.io/monumenta-java-shard
docker push monumenta-docker.injic.io/monumenta-basic-ssh
docker push monumenta-docker.injic.io/monumenta-automation-bot
```

# Kubernetes config:

```
kubectl create secret docker-registry regcred --docker-server=monumenta-docker.injic.io --docker-username=monumenta --docker-password=<password>

cd secrets
kubectl create secret generic automation-bot-build-config --from-file=config.yml
```
