#!/bin/sh
UID=${UID} GID=${GID} docker compose up "$@"
