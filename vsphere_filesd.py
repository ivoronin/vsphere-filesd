import json
import logging
import os
import os.path
from time import sleep
import tempfile
import requests
import urllib3
from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vapi.std_client import DynamicID
import com.vmware.vapi.std.errors_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def output(vms, filename):
    logging.info("Writing to %s (%i vms)", filename, len(vms))
    data = json.dumps(vms, indent=4, sort_keys=True)
    tmp_dir = os.path.dirname(filename)
    tmp_prefix = "%s." % os.path.basename(filename)
    (tmp_fd, tmp_name) = tempfile.mkstemp(prefix=tmp_prefix, dir=tmp_dir)
    os.write(tmp_fd, data.encode('utf-8'))
    os.fsync(tmp_fd)
    os.close(tmp_fd)
    os.rename(tmp_name, filename)


def discover(server, username, password, insecure, include, filename):
    logging.info("Starting discovery cycle")

    session = requests.session()

    if insecure:
        session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    vsphere_client = create_vsphere_client(server=server, username=username, password=password, session=session)

    tag_names = {}
    tag_category_ids = {}
    for tag_id in vsphere_client.tagging.Tag.list():
        tag = vsphere_client.tagging.Tag.get(tag_id)
        tag_names[tag.id] = tag.name
        tag_category_ids[tag.id] = tag.category_id

    category_names = {}
    for category_id in vsphere_client.tagging.Category.list():
        category = vsphere_client.tagging.Category.get(category_id)
        category_names[category.id] = category.name

    vms = []
    for vm in vsphere_client.vcenter.VM.list():
        if vm.power_state != 'POWERED_ON':
            logging.info("Skipping %s, because of the power state (%s)", vm.name, vm.power_state)
            continue

        try:
            identity = vsphere_client.vcenter.vm.guest.Identity.get(vm.vm)
        except com.vmware.vapi.std.errors_client.ServiceUnavailable:
            logging.info("Skipping %s, cannot get guest identity (check if vm tools are running)", vm.name)
            continue

        if include:
            dynamic_id = DynamicID(type='VirtualMachine', id=vm.vm)
            for tag_id in vsphere_client.tagging.TagAssociation.list_attached_tags(dynamic_id):
                tag_name = tag_names[tag_id]
                category_name = category_names[tag_category_ids[tag_id]]
                for category_tag in include:
                    if category_tag == f'{category_name}:{tag_name}':
                        break
                else:
                    # Current tag does not match, continue to the next one
                    continue
                # Current tag matches filter, exit loop
                break
            else:
                logging.info("Skipping %s, tags do not match", vm.name)
                # All tags does not match, contnue to the next vm
                continue

        logging.info("Including %s (%s)", vm.name, identity.ip_address)
        vms.append({
            'targets': [vm.name],
            'labels': {
                'id': vm.vm,
                'guest_name': identity.name,
                'guest_family': identity.family,
                'guest_host_name': identity.host_name,
                'guest_ip_address': identity.ip_address,
            }
        })

    output(vms, filename)


def getenv(name, default=None, required=False):
    value = os.environ.get(name)
    if not value and required:
        raise Exception(f'{name} is not set')
    if not value and default:
        return default
    return value


def main():
    server = getenv('VSPHERE_HOST', required=True)
    username = getenv('VSPHERE_USER', required=True)
    password = getenv('VSPHERE_PASSWORD', required=True)
    insecure = getenv('VSPHERE_IGNORE_SSL', False)
    include = getenv('INCLUDE_TAGS', '').split()
    filename = getenv('OUTPUT_FILENAME', '/etc/prometheus/vsphere.json')
    interval = int(getenv('DISCOVERY_INTERVAL', '300'))

    while True:
        discover(server, username, password, insecure, include, filename)
        sleep(interval)


if __name__ == '__main__':
    main()
