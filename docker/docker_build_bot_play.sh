#!/bin/bash

pushd ../rust
./build.sh || exit $?
popd
docker build .. --file automation-bot.Dockerfile -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-automation-bot-play --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-automation-bot-play
