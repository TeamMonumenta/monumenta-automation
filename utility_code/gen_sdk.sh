#!/bin/sh

rm -rf purgatory sdk1 sdk2 velocity server_config
cd monumenta-automation
git pull
cd ..
python3 monumenta-automation/utility_code/copy_server_config.py
python3 monumenta-automation/utility_code/gen_sdk_config.py purgatory sdk1 sdk2 velocity
python3 monumenta-automation/utility_code/fix_sdk_symlinks.py

cp monumenta-automation/docker/sdk/docker-compose.yml .
cp monumenta-automation/docker/sdk/rabbitmq.conf .
mkdir redis
mkdir redis/data
cp monumenta-automation/docker/sdk/redis.conf redis/redis.conf
