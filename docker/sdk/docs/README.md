# Monumenta SDK

**WARNING: This is an IN-DEV unstable version of the SDK! Expect bugs!**

## Running
This SDK uses *docker*, which can only be run on linux or mac (?). If you are using windows, use [wsl2](https://learn.microsoft.com/en-us/windows/wsl/install)

### Download docker
- Arch: `# pacman -S docker docker-compose`
- Ubuntu/Debian: `# sudo apt-get install docker docker-compose-plugin`
- RPM based: `# sudo yum install docker docker-compose-plugin`
- MacOS: [here](https://docs.docker.com/desktop/setup/install/mac-install/)

### Start container
First run:
```sh
$ UID=${UID} GID=${GID} docker compose up redis rabbitmq --detach
```

Then you can start shards (`velocity`, `sdk1`, `sdk2`) with:
```sh
$ UID=${UID} GID=${GID} docker compose up [shard_name] --detach
```

You may stop containers with `docker compose down`. Make sure to always include the `UID=${UID} GID=${GID}` before any command.

You may need to run docker as root, in which case you should use `sudo`, or [enable non-root users to access docker](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)

## Contributing

The SDK enables you to contribute to monumenta, by giving you a development enviroment where you can test many things.

Plugin changes should be submitted as a pull request.

Links:
- The main plugin: https://github.com/TeamMonumenta/monumenta-plugins-public
- Automation repo: https://github.com/TeamMonumenta/monumenta-automation
