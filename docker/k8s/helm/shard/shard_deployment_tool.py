#!/usr/bin/env python3

from pathlib import Path
import json
import sys
import subprocess
import tempfile
import re
import yaml


with open("shard_deployment_tool_config.yaml", "r", encoding="utf-8-sig") as fp:
    tool_config = yaml.load(fp, Loader=yaml.FullLoader)

shard_config = tool_config["shard_config"]
namespace_defaults = tool_config["namespace_defaults"]
node_info = tool_config["node_info"]

# "node" uses abbreviated node names. This is the map back to full names:
abbrev_node_to_full = {name: node["full_name"] for name, node in node_info.items()}

# Node memory totals
for node in node_info.values():
    total_huge_page_size_GB = node["huge_pages"] * node["huge_page_size_kB"] / 1024.0 / 1024.0
    total_non_huge_size_GB = node["mem_total_kB"] / 1024.0 / 1024.0 - total_huge_page_size_GB
    node["total_huge_page_size_GB"] = total_huge_page_size_GB
    node["total_non_huge_size_GB"] = total_non_huge_size_GB


RE_NUMBER = re.compile('''[0-9]+''')
RE_NOT_NUMBER = re.compile('''[^0-9]+''')


def usage():
    sys.exit(f'''Usage: {sys.argv[0]} <action> <namespace> <shard>
<action> can be one of these:
    print - Generates the YAML deployment and prints it out
    memoryusage - Displays the memory usage on each node
    exportmemoryjson - Generates JSON for the memory usage of each node and prints it out
    apply - Generates and applies the deployment, possibly creating or restarting the existing shard
    applyall - Generates and applies all deployments for this namespace with names matching the regex given by <shard>. Use '.' to match all.
    delete - Generates and then deletes the deployment, stopping shard if it is running
    deleteall - Generates and deletes all deployments for this namespace with names matching the regex given by <shard>. Use '.' to match all.
    test - Tests the config for the specified shard
    testall - Tests the config for the specified shards. Use '.' to match all.
    matchall - Prints out what shards match the arguments supplied which would be executed by applyall/deleteall/testall (without actually running)
''')


def run_helm_for_shard(namespace, shard):
    if shard not in shard_config:
        sys.exit(f"Unable to find shard {shard} in shard_config, must be one of [{','.join(shard_config.keys())}]")

    shard_conf = shard_config[shard]
    if namespace not in shard_conf:
        sys.exit(f"Shard {shard} does not have config for namespace {namespace}")

    # Get the values just for this namespace
    shard_namespaced = shard_conf[namespace]

    # Start with the defaults for this namespace
    output_conf = namespace_defaults[namespace].copy()

    # Copy over all the values set for this shard/namespace
    for key in shard_namespaced:
        output_conf[key] = shard_namespaced[key]

    # Set additional required values from the context
    output_conf["name"] = shard
    output_conf["namespace"] = namespace
    node = shard_namespaced["node"]
    output_conf["nodeFull"] = abbrev_node_to_full.get(node, f"monumenta-bad-lookup-{node}")
    if "memGB" in output_conf:
        output_conf["memMB"] = output_conf["memGB"] * 1024

    # Create a list of all the key=value pairs
    vals = []
    for key, value in output_conf.items():
        vals.append(f"{key}={value}")

    # Run helm to generate the new shard template
    proc = subprocess.run(["helm", "template", ".", "--set", ",".join(vals)], stdout=subprocess.PIPE, check=False)

    return proc


def perform_shard_action(action, namespace, shard):
    proc = run_helm_for_shard(namespace, shard)

    # Handle whatever action the user specified
    if action == "print":
        print(proc.stdout.decode('utf-8'))
    elif action == "apply":
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(proc.stdout)
            fp.flush()
            subprocess.run(["kubectl", "apply", "-f", fp.name], check=False)
    elif action == "delete":
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(proc.stdout)
            fp.flush()
            subprocess.run(["kubectl", "delete", "-f", fp.name], check=False)
    elif action == "test":
        test_shard(namespace, shard)


def test_shard(namespace, shard):
    found_problem = False

    shard_info = shard_config[shard]
    shard_namespace_info = shard_info[namespace]
    node = shard_namespace_info["node"]


    secrets_dir = Path('.').absolute().parent.parent.parent / 'secrets'

    shard_dir = None
    if namespace == 'build':
        bot_config_path = secrets_dir / namespace / node / 'config.yml'
        if not bot_config_path.exists():
            print(f"{namespace} {shard}: No config for {namespace} {node} bot secret", file=sys.stderr)
            found_problem = True

        else:
            with open(bot_config_path, 'r', encoding='utf-8-sig') as fp:
                bot_config = yaml.load(fp, Loader=yaml.FullLoader)

                shard_dir = bot_config["shards"].get(shard, None)
                if shard_dir is None:
                    print(f"{namespace} {shard}: Path not specified in {namespace} bot secret", file=sys.stderr)
                    found_problem = True

    elif namespace in ('stage', 'volt'):
        bot_config_path = secrets_dir / namespace / node / 'config.yml'
        if not bot_config_path.exists():
            print(f"{namespace} {shard}: No config for {namespace} {node} bot secret", file=sys.stderr)
            found_problem = True

        else:
            with open(bot_config_path, 'r', encoding='utf-8-sig') as fp:
                bot_config = yaml.load(fp, Loader=yaml.FullLoader)

                shard_dir = bot_config["shards"].get(shard, None)
                if shard_dir is None:
                    print(f"{namespace} {shard}: Path not specified in {namespace} {node} bot secret", file=sys.stderr)
                    found_problem = True

    elif namespace == 'play':
        bot_config_path = secrets_dir / namespace / node / 'config.yml'
        if not bot_config_path.exists():
            print(f"{namespace} {shard}: No config for {namespace} {node} bot secret", file=sys.stderr)
            found_problem = True

        else:
            queue_name = None
            with open(bot_config_path, 'r', encoding='utf-8-sig') as fp:
                bot_config = yaml.load(fp, Loader=yaml.FullLoader)
                queue_name = bot_config["rabbitmq"]["name"]

                shard_dir = bot_config["shards"].get(shard, None)
                if shard_dir is None:
                    print(f"{namespace} {shard}: Path not specified in {namespace} {node} bot secret", file=sys.stderr)
                    found_problem = True

            stage_required = shard.endswith("-1") or not shard[-1].isdigit()
            stage_found = False
            for stage_node in node_info:
                bot_config_path = secrets_dir / 'stage' / stage_node / 'config.yml'
                if not bot_config_path.is_file():
                    continue

                with open(bot_config_path, 'r', encoding='utf-8-sig') as fp:
                    bot_config = yaml.load(fp, Loader=yaml.FullLoader)

                    stage_source = bot_config.get("stage_source", {}).get(node, {})
                    if shard not in stage_source.get("shards", []):
                        continue

                    stage_found = True

                    if stage_source.get("queue_name", None) != queue_name or queue_name is None:
                        print(f"{namespace} {shard}: RabbitMQ queue name set incorrectly for play bot ({node}) or stage bot ({stage_node})", file=sys.stderr)
                        found_problem = True

            if stage_required and not stage_found:
                print(f"{namespace} {shard}: Not listed as a stage source", file=sys.stderr)
                found_problem = True


    if shard_dir is not None:
        shard_dir = Path(shard_dir)
        if not shard_dir.is_dir():
            print(f"{namespace} {shard}: Path not found: {shard_dir}", file=sys.stderr)
            found_problem = True


    if found_problem:
        sys.exit("One or more config errors were found")

    print(f"{namespace} {shard}: OK")


def get_shard_deployment(namespace, shard):
    proc = run_helm_for_shard(namespace, shard)

    yaml_data = []
    document_data = ''
    for line in proc.stdout.decode('utf-8').splitlines(keepends=True):
        if line.rstrip().startswith('---'):
            if len(document_data) != 0:
                yaml_data.append(yaml.load(document_data, Loader=yaml.FullLoader))
                document_data = ''
            continue

        document_data += line

    yaml_data.append(yaml.load(document_data, Loader=yaml.FullLoader))

    return yaml_data


def get_deployment_hugepage_memory_limit_GB(deployment):
    result = 0
    for document in deployment:
        try:
            for container in document["spec"]["template"]["spec"]["containers"]:
                result += parse_data_size_GB(container["resources"]["limits"]["hugepages-2Mi"])
        except KeyError:
            pass
    return result


def get_deployment_normal_memory_limit_GB(deployment):
    result = 0
    for document in deployment:
        try:
            for container in document["spec"]["template"]["spec"]["containers"]:
                result += parse_data_size_GB(container["resources"]["limits"]["memory"])
        except KeyError:
            pass
    return result


def parse_data_size_GB(data_size):
    if isinstance(data_size, (int, float)):
        return data_size

    data_size = data_size.lower()
    if data_size.endswith('b'):
        data_size = data_size[:-1]
    if data_size.endswith('i'):
        data_size = data_size[:-1]

    data_size = data_size.strip()

    multiplier = 1.0
    if data_size.endswith('k'):
        multiplier *= 1024.0 * 1024.0
        data_size = data_size[:-1]
    elif data_size.endswith('m'):
        multiplier *= 1024.0
        data_size = data_size[:-1]
    elif data_size.endswith('g'):
        data_size = data_size[:-1]
    elif data_size.endswith('t'):
        multiplier /= 1024.0
        data_size = data_size[:-1]

    return float(data_size.strip()) / multiplier


def natural_sort(key):
    if not isinstance(key, str):
        return key

    result = []
    while len(key) > 0:
        match = RE_NUMBER.match(key)
        if match:
            result.append(int(key[:match.end()]))
            key = key[match.end():]
            continue

        match = RE_NOT_NUMBER.match(key)
        if match:
            part = key[:match.end()]
            if part.startswith('.'):
                result.append('.')
                part = part[1:]
            result.append(part.lower())
            result.append(part)
            key = key[match.end():]
            continue

        print('Somehow not a number nor a non-number?')
        print(repr(key))
        result.append(key)
        break

    return result


def print_memory_usage():
    node_normal_usages = {}
    node_hugepage_usages = {}
    namespace_normal_usages = {}
    namespace_hugepage_usages = {}
    namespaces = set()
    for shard_id, shard in shard_config.items():
        for namespace, namespace_info in shard.items():
            deployment = None
            try:
                deployment = get_shard_deployment(namespace, shard_id)
            except Exception as ex:
                print(f"Failed to load deployment for {namespace} {shard_id}", file=sys.stderr)
                raise ex

            namespaces.add(namespace)
            normal_GB = get_deployment_normal_memory_limit_GB(deployment)
            hugepage_GB = get_deployment_hugepage_memory_limit_GB(deployment)

            node = namespace_info["node"]
            if node not in node_hugepage_usages:
                node_normal_usages[node] = 0.0
                node_hugepage_usages[node] = 0.0
            node_normal_usages[node] += normal_GB
            node_hugepage_usages[node] += hugepage_GB

            if namespace not in namespace_hugepage_usages:
                namespace_normal_usages[namespace] = {}
                namespace_hugepage_usages[namespace] = {}
            if node not in namespace_hugepage_usages[namespace]:
                namespace_normal_usages[namespace][node] = 0.0
                namespace_hugepage_usages[namespace][node] = 0.0
            namespace_normal_usages[namespace][node] += normal_GB
            namespace_hugepage_usages[namespace][node] += hugepage_GB

    header_width = max(len('Hugepages:'), len('Normal:'), len('Total:'), len('System:'), len('Remaining:'), *[len(namespace) for namespace in namespaces])
    column_width = max(8 + len(' GB'), *[len(node) for node in node_hugepage_usages])

    header = 'Normal:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_normal_usages.keys(), key=natural_sort):
        print(f' │ {node:<{column_width}}', end='')
    print('')

    print('─' * header_width, end='')
    for node in sorted(node_normal_usages.keys(), key=natural_sort):
        print('─┼─' + '─'*column_width, end='')
    print('')

    for namespace in sorted(namespaces, key=natural_sort):
        namespace_info = namespace_normal_usages[namespace]
        print(f'{namespace:<{header_width}}', end='')
        for node in sorted(node_normal_usages.keys(), key=natural_sort):
            memGB = namespace_info.get(node, 0.0)
            preformatted_entry = f'{memGB:8.2f} GB'
            print(f' │ {preformatted_entry:>{column_width}}', end='')
        print('')

    print('─' * header_width, end='')
    for node in sorted(node_normal_usages.keys(), key=natural_sort):
        print('─┼─' + '─'*column_width, end='')
    print('')

    header = 'Total:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_normal_usages.keys(), key=natural_sort):
        memGB = node_normal_usages[node]
        preformatted_entry = f'{memGB:8.2f} GB'
        print(f' │ {preformatted_entry:>{column_width}}', end='')
    print('')

    header = 'System:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_normal_usages.keys(), key=natural_sort):
        memGB = node_info.get(node, {}).get("total_non_huge_size_GB", 0.0)
        preformatted_entry = f'{memGB:8.2f} GB'
        print(f' │ {preformatted_entry:>{column_width}}', end='')
    print('')

    header = 'Remaining:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_normal_usages.keys(), key=natural_sort):
        memGB = node_info.get(node, {}).get("total_non_huge_size_GB", 0.0) - node_normal_usages[node]
        preformatted_entry = f'{memGB:8.2f} GB'
        print(f' │ {preformatted_entry:>{column_width}}', end='')
    print('')

    print('─' * header_width, end='')
    for node in sorted(node_normal_usages.keys(), key=natural_sort):
        print('─┼─' + '─'*column_width, end='')
    print('')

    header = 'Hugepages:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_hugepage_usages.keys(), key=natural_sort):
        print(f' │ {node:<{column_width}}', end='')
    print('')

    print('─' * header_width, end='')
    for node in sorted(node_hugepage_usages.keys(), key=natural_sort):
        print('─┼─' + '─'*column_width, end='')
    print('')

    for namespace in sorted(namespaces, key=natural_sort):
        namespace_info = namespace_hugepage_usages[namespace]
        print(f'{namespace:<{header_width}}', end='')
        for node in sorted(node_hugepage_usages.keys(), key=natural_sort):
            memGB = namespace_info.get(node, 0.0)
            preformatted_entry = f'{memGB:8.2f} GB'
            print(f' │ {preformatted_entry:>{column_width}}', end='')
        print('')

    print('─' * header_width, end='')
    for node in sorted(node_hugepage_usages.keys(), key=natural_sort):
        print('─┼─' + '─'*column_width, end='')
    print('')

    header = 'Total:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_hugepage_usages.keys(), key=natural_sort):
        memGB = node_hugepage_usages[node]
        preformatted_entry = f'{memGB:8.2f} GB'
        print(f' │ {preformatted_entry:>{column_width}}', end='')
    print('')

    header = 'System:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_hugepage_usages.keys(), key=natural_sort):
        memGB = node_info.get(node, {}).get("total_huge_page_size_GB", 0.0)
        preformatted_entry = f'{memGB:8.2f} GB'
        print(f' │ {preformatted_entry:>{column_width}}', end='')
    print('')

    header = 'Remaining:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_hugepage_usages.keys(), key=natural_sort):
        memGB = node_info.get(node, {}).get("total_huge_page_size_GB", 0.0) - node_hugepage_usages[node]
        preformatted_entry = f'{memGB:8.2f} GB'
        print(f' │ {preformatted_entry:>{column_width}}', end='')
    print('')


def export_memory_to_json():
    namespaces = set()
    nodes = {}
    for shard_id, shard in shard_config.items():
        for namespace, namespace_info in shard.items():
            deployment = None
            try:
                deployment = get_shard_deployment(namespace, shard_id)
            except Exception as ex:
                print(f"Failed to load deployment for {namespace} {shard_id}", file=sys.stderr)
                raise ex

            node = namespace_info["node"]
            namespaces.add(namespace)
            shard_json = {
                "namespace": namespace,
                "shard": shard_id,
                "normal_GB": get_deployment_normal_memory_limit_GB(deployment),
                "hugepage_GB": get_deployment_hugepage_memory_limit_GB(deployment),
            }

            if node not in nodes:
                nodes[node] = {
                    "max_memory_GB": 0.0,
                    "max_hugepage_GB": 0.0,
                    "shards": []
                }

            nodes[node]["shards"].append(shard_json)

    for node, node_values in node_info.items():
        if node not in nodes:
            nodes[node] = {
                "max_memory_GB": 0.0,
                "max_hugepage_GB": 0.0,
                "shards": []
            }

        nodes[node]["max_memory_GB"] = node_values["total_huge_page_size_GB"]
        nodes[node]["max_hugepage_GB"] = node_values["total_non_huge_size_GB"]

    print(json.dumps({
        "namespaces": list(namespaces),
        "nodes": nodes,
    }, indent=2, ensure_ascii=False, sort_keys=True))


if len(sys.argv) == 1:
    usage()

if len(sys.argv) >= 2:
    action = sys.argv[1]
    if action == "memoryusage":
        print_memory_usage()
        sys.exit()
    if action == "exportmemoryjson":
        export_memory_to_json()
        sys.exit()

if len(sys.argv) != 4:
    usage()

namespace = sys.argv[2]
shard = sys.argv[3]

if action in ["print", "apply", "delete", "test"]:
    perform_shard_action(action, namespace, shard)
elif action in ["applyall", "deleteall", "testall", "matchall"]:
    # Shard is a regex for "all" operations
    shard_re = re.compile(shard)
    shards = [s for s in shard_config if ((namespace in shard_config[s]) and shard_re.match(s))]
    for s in shards:
        if action == "applyall":
            perform_shard_action("apply", namespace, s)
        elif action == "deleteall":
            perform_shard_action("delete", namespace, s)
        elif action == "testall":
            test_shard(namespace, s)
        else:
            print(s)

else:
    usage()
