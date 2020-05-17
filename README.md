# vsphere-filesd
Prometheus file discovery service for VMware vSphere VMs

Tested with VMware vCenter 7.0

## Docker
A Docker container for vsphere-filesd is available from Docker Hub
```shell
docker run -d --name vsphere-filesd \
  -e VSPHERE_HOST=vcenter01 \
  -e VSPHERE_USER=Administrator@vsphere.local \
  -e VSPHERE_PASSWORD=<password> \
  -e VSPHERE_IGNORE_SSL=1 \ # default is 0
  -e DISCOVERY_INTERVAL=600 \ # default is 300
  -e INCLUDE_TAGS="role:db role:app" \ # "category:tag ...", by default all vms are included in the output
  -e OUTPUT_FILENAME=/data/vsphere.json \ # default is /etc/prometheus/vsphere.json
  -v /etc/prometheus:/data \
  ivoronin/vsphere-filesd:latest
``` 

## Example Prometheus config
```yaml
scrape_configs:
  #
  # https://github.com/prometheus/node_exporter
  #
  - job_name: 'vshere_node'
    file_sd_configs:
      - files:
          - /etc/prometheus/vsphere.json
    relabel_configs:
      - source_labels: [guest_family]
        regex: "LINUX"
        action: keep
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [guest_ip_address]
        target_label:  __address__
        replacement:   '${1}:9100'
    #
    # https://github.com/martinlindhe/wmi_exporter
    #
  - job_name: 'vshere_wmi'
    file_sd_configs:
      - files:
          - /etc/prometheus/vsphere.json
    relabel_configs:
      - source_labels: [guest_family]
        regex: "WINDOWS"
        action: keep
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [guest_ip_address]
        target_label:  __address__
        replacement:   '${1}:9182'
  - job_name: 'vsphere_icmp'
    metrics_path: /probe
    params:
      module: [icmp]
    file_sd_configs:
      - files:
          - /etc/prometheus/vsphere.json
    relabel_configs:
      - source_labels: [guest_ip_address]
        target_label: __param_target
      - source_labels: [__address__]
        target_label: instance
      - target_label: __address__
        replacement: 'blackbox-exporter:9115'
```

## Example output
```json
[
    {
        "labels": {
            "guest_family": "LINUX",
            "guest_host_name": "db01",
            "guest_ip_address": "10.0.1.66",
            "guest_name": "UBUNTU_64",
            "id": "vm-6829",
            "tags": "role:db,backup:daily"
        },
        "targets": [
            "db01"
        ]
    },
    {
        "labels": {
            "guest_family": "WINDOWS",
            "guest_host_name": "app01"
            "guest_ip_address": "10.0.1.68",
            "guest_name": "WINDOWS_9_SERVER_64",
            "id": "vm-7502",
            "tags": "role:app"
        },
        "targets": [
            "app01"
        ]
    }
]
```
