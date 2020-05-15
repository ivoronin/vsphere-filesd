# vsphere-filesd
Prometheus file discovery service for VMware vSphere VMs
Tested with VMware vCenter 7.0

## Docker
A Docker container for vsphere-filesd is available from Docker Hub
```shell
docker run -d --name vsphere-filesd \
  -e VSPHERE_SERVER=vcenter01 \
  -e VSPHERE_USERNAME=Administrator@vsphere.local \
  -e VSPHERE_PASSWORD=<password> \
  -e VSPHERE_INSECURE=1 \ # default is 0
  -e DISCOVERY_INTERVAL=600 \ # default is 300
  -e INCLUDE_TAGS="role:db role:app" \ # "category:tag ...", by default all vms are included in the output
  -e OUTPUT_FILENAME=/data/vsphere.json \ # default is /etc/prometheus/vsphere.json
  -v /etc/prometheus:/data \
  ivoronin/vsphere-filesd:latest
``` 

## Example Prometheus config
```yaml
scrape_configs:
  - job_name: 'vshere_node'
    file_sd_configs:
      - files:
          - /etc/prometheus/vsphere.json
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [guest_ip_address]
        target_label:  __address__
        replacement:   '${1}:9100'
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
