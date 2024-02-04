#!/bin/bash

pushd ../rust
./build.sh || exit $?
popd
docker build .. --file automation-bot.Dockerfile -t ghcr.io/teammonumenta/monumenta-automation/monumenta-automation-bot-volt --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push ghcr.io/teammonumenta/monumenta-automation/monumenta-automation-bot-volt
