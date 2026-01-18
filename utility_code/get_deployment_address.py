#!/usr/bin/env python3
"""Gets the deployment address of a pod"""

import argparse
import json
import subprocess
import sys


def get_deployment_address(namespace, deployment_name):
    kube_subprocess = subprocess.run(['/home/epic/bin/kubectl', 'get', 'pods', '-n', namespace, '-o', 'json'], capture_output=True)
    kube_stdout = kube_subprocess.stdout.decode(encoding='utf-8').strip()

    kube_data = json.loads(kube_stdout)["items"]

    for deployment in kube_data:
        metadata = deployment.get("metadata", None)
        if not metadata:
            continue
        labels = metadata.get("labels", None)
        if not labels:
            continue
        app = labels.get("app", None)
        if app != deployment_name:
            continue

        status = deployment.get("status", None)
        if status is None:
            continue
        pod_ip = status.get("podIP", None)
        if pod_ip is None:
            continue

        return pod_ip

    return None


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('namespace')
    arg_parser.add_argument('deployment')
    args = arg_parser.parse_args()

    namespace = args.namespace
    deployment = args.deployment

    address = get_deployment_address(namespace, deployment)
    if address is None:
        sys.exit(1)
    print(address)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
