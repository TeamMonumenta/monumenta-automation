# SDK Generation

SDK generation relies on several scripts:
- `utility_code/copy_server_config.py` - copies server configuration
- `utility_code/gen_sdk_config.py` - generates sdk config (todo: merge into `gen_server_config.py`)
- `utility_code/gen_sdk.sh` - generates the sdk itself
- `utility_code/fix_sdk_symlinks.py` - un-symlinks some things

Most of the "static" data for the SDK is tracked in automation under `docker/sdk`.
