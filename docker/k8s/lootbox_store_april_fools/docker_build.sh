#!/bin/bash

docker build . -t docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-store && docker push docker.pkg.github.com/teammonumenta/monumenta-automation/monumenta-store
