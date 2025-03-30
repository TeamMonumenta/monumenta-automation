# ZFS Snapshot Manager

A Golang daemon that manages ZFS snapshots with an HTTP + JSON (REST API) interface and YAML-based configuration.

## Configuration File
Example `config.yaml`:
```yaml
# Port the server should listen on
port: 8080

# Regular expressions describing the names of datasets that can be manipulated
# Note that a dataset will match child datasets too if $ is not used to indicate
# the end of the name
allowed_dataset_names:
  # Matches pool/home/user and pool/home/user/child
  - ^pool/home/user
  # Matches just pool/home and NOT pool/home/user
  - ^pool/home$

# Regular expressions describing the names of snapshots that can be manipulated
# All snapshots will be returned via the "list" command
# "create" and "delete" can only manipulate snapshots that match the rules here
allowed_snapshot_names:
  - ^zfs-auto-snap_hourly-
```

## Running the Server
```bash
go run cmd/main.go --config ./config.yaml
```

## API Specification:
All API methods return JSON on success, or an HTTP error on failure. No JSON is returned on failure.

### free
```bash
curl "http://localhost:8080/free?dataset=ipool/home"
```
Returns free space available to that pool in gigabytes
```json
{
  "free": 123
}
```

### list
```bash
curl "http://localhost:8080/list?dataset=ipool/home"
```
```json
{
  "dataset": "pool/home",
  "snapshots": [
    {
      "name": "move-to-new-system-pre-configure-2022-09-25",
      "refer": "2.02G",
      "used": "0B"
    },
    {
      "name": "zfs-auto-snap_frequent-2025-03-29-2300",
      "refer": "1.83G",
      "used": "0B"
    }
  ]
}
```

### create
```bash
curl "http://localhost:8080/create?dataset=ipool/home&snapshot=zfs-auto-snap_hourly-2025-03-29-1200"
```
```json
{"status":"success"}
```

### delete
```bash
curl "http://localhost:8080/delete?dataset=ipool/home&snapshot=zfs-auto-snap_hourly-2025-03-29-1200"
```
```json
{"status":"success"}
```
