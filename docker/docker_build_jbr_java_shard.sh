#!/bin/bash

docker build .. --file java-shard-21-jbr.Dockerfile -t ghcr.io/teammonumenta/monumenta-automation/monumenta-java-jbr-shard-21 --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push ghcr.io/teammonumenta/monumenta-automation/monumenta-java-jbr-shard-21
