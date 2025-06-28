# Monumenta SDK

**WARNING: This SDK is under active development and may be unstable. Expect bugs.**

## Getting Started

This SDK uses **Docker** and works best on *Linux* or *macOS*. On *Windows*, use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install).

### Install Docker

- **Arch:** `sudo pacman -S docker docker-compose`
- **Debian/Ubuntu:** `sudo apt-get install docker docker-compose-plugin`
- **RPM-based:** `sudo yum install docker docker-compose-plugin`
- **macOS:** [Install Docker](https://docs.docker.com/desktop/setup/install/mac-install)

> You may need to run Docker as root (`sudo`) or [enable non-root access](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

### Start the Environment

1. Start core services:

```sh
UID=${UID} GID=${GID} docker compose up redis rabbitmq --detach
```

2. Start a shard (`velocity`, `sdk1`, `sdk2`, etc.):

```sh
UID=${UID} GID=${GID} docker compose up [shard_name] --detach
```

3. Stop everything:

```sh
docker compose down
```

Always include `UID=${UID} GID=${GID}` when starting containers.

## Contributing

This SDK provides a development environment for testing and contributing to Monumenta.

Submit plugin changes via pull request.

Improvements to the SDK itself should be submitted to the automation repo.

- Relevant repositories:
  - [Monumenta Plugins](https://github.com/TeamMonumenta/monumenta-plugins-public)
  - [Automation](https://github.com/TeamMonumenta/monumenta-automation)


## Licensing 

- Monumenta plugins and automation is licensed under AGPL.
- Other plugins are distributed according to their own licenses.
- The SDK itself is licensed under AGPL.
