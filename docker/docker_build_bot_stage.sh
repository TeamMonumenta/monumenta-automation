#!/bin/bash

docker build .. --file automation-bot.Dockerfile -t monumenta-docker.injic.io/monumenta-automation-bot-stage --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push monumenta-docker.injic.io/monumenta-automation-bot-stage
