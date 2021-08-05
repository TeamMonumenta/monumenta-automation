#!/usr/bin/env python3

import os
import yaml

shards_config = None
if "SHARD_CONFIG" in os.environ and os.path.isfile(os.environ["SHARD_CONFIG"]):
    shard_config_path = os.environ["SHARD_CONFIG"]
    with open(shard_config_path, 'r') as ymlfile:
        shards_config = yaml.load(ymlfile, Loader=yaml.FullLoader)
