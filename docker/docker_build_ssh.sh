#!/bin/bash

docker build . --file basic-ssh.Dockerfile -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-basic-ssh --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-basic-ssh
docker build . --file basic-ssh-dev.Dockerfile -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-basic-ssh-dev --build-arg USERNAME=epic --build-arg UID=1000 --build-arg GID=1000 && docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-basic-ssh-dev
