#!/usr/bin/env python3

import asyncio
from pprint import pprint
from lib_py3.lib_k8s import KubernetesManager

async def main():
    k8s = KubernetesManager("volt")
    pprint(await k8s.list())

asyncio.run(main())
