#!/bin/bash

docker build .. --file java-shard-25.Dockerfile -t ghcr.io/teammonumenta/monumenta-automation/monumenta-java-shard-25 --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push ghcr.io/teammonumenta/monumenta-automation/monumenta-java-shard-25
