# Building images

```
docker build . --file java-shard.Dockerfile -t monumentammo/monumenta-java-shard --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000
docker build . --file basic-ssh.Dockerfile -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-basic-ssh --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 --build-arg PASS='<thepassword>'
docker build . --file basic-ssh.Dockerfile -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-build-ssh --build-arg USERNAME=builder --build-arg UID=1000 --build-arg GID=1000 --build-arg PASS='<thepassword>'
docker build .. --file automation-bot.Dockerfile -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-automation-bot --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000
```

# Logging in to the docker registry

```
docker login docker.pkg.github.com
```

# Push

```
docker push monumentammo/monumenta-java-shard
docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-basic-ssh
docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-build-ssh
docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-automation-bot
```

# Kubernetes config for registry:

```
kubectl create secret docker-registry githubcred -n build --docker-server=docker.pkg.github.com --docker-username=monumenta --docker-password=<password>
```

# Changing the automation bot's config
```
cd secrets/build
kubectl create secret generic automation-bot-config -n build --from-file=config.yml
```
