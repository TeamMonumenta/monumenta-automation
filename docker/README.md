# Building images

Use the image build scripts in this directory

# Logging in to the docker registry

```
docker login docker.pkg.github.com
```

# Push

```
docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-java-shard
docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-basic-ssh
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
