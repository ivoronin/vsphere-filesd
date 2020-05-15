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
