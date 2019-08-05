# Building images

```
docker build . --file java-shard.Dockerfile -t monumenta-docker.injic.io/monumenta-java-shard --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000
docker build . --file basic_ssh.Dockerfile -t monumenta-docker.injic.io/monumenta-basic-ssh --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 --build-arg PASS=<thepassword>
docker build .. --file automation-bot.Dockerfile -t monumenta-docker.injic.io/monumenta-automation-bot --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000
```

Building the `monumenta-dev-environment` image requires getting Combustible/Byron's configscripts repo to build.
```
git clone git@github.com:Combustible/configscripts.git configscripts.formonumenta
cd configscripts.formonumenta
git checkout for_monumenta
docker build . -t monumenta-docker.injic.io/monumenta-dev-environment --build-arg USERNAME=epic --build-arg GIT_NAME="Monumenta" --build-arg GIT_EMAIL=MonumentaMMO@gmail.com --build-arg UID=1000 --build-arg GID=1000 --build-arg DOCKER_GID=999
```

# Logging in to the docker registry

```
docker login monumenta-docker.injic.io
```

# Push

```
docker push monumenta-docker.injic.io/monumenta-java-shard
docker push monumenta-docker.injic.io/monumenta-basic-ssh
docker push monumenta-docker.injic.io/monumenta-automation-bot
docker push monumenta-docker.injic.io/monumenta-dev-environment
```

# Kubernetes config for registry:

```
kubectl create secret docker-registry regcred -n build --docker-server=monumenta-docker.injic.io --docker-username=monumenta --docker-password=<password>
```

# Changing the automation bot's config
```
cd secrets/build
kubectl create secret generic automation-bot-config -n build --from-file=config.yml
```
