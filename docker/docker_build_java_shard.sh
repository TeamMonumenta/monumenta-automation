#!/bin/bash

docker build .. --file java-shard.Dockerfile -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-java-shard --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-java-shard
