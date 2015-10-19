#!/usr/bin/env python

"""
Takes cluster.yaml and writes out an Ansible inventory file for the cluster.
"""

import argparse
import jinja2
import os
import sys
import yaml


INVENTORY_TEMPLATE = """[localhost]
127.0.0.1 ansible_connection=local

[{{ cluster_name }}:vars]
ansible_ssh_user={{ cluster_ssh_user }}
{% if cluster_hardware_type %}
hardware_type={{ cluster_hardware_type }}
{% endif %}

[{{ cluster_name }}:children]
{{ cluster_name }}-bootstraps
{{ cluster_name }}-cluster

[{{ cluster_name }}-cluster:children]
{{ cluster_name }}-headnodes
{{ cluster_name }}-worknodes
{{ cluster_name }}-ephemeral-worknodes
{{ cluster_name }}-monitoringnodes

[{{ cluster_name }}-worknodes]
{% for item in worknodes|dictsort %}
{% if cluster_hardware_type %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }}
{% else %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }} hardware_type={{ item[1].hardware_type }}
{% endif %}
{% endfor %}

[{{ cluster_name }}-ephemeral-worknodes]
{% for item in eworknodes|dictsort %}
{% if cluster_hardware_type %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }}
{% else %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }} hardware_type={{ item[1].hardware_type }}
{% endif %}
{% endfor %}

[{{ cluster_name }}-headnodes]
{% for item in headnodes|dictsort %}
{% if cluster_hardware_type %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }}
{% else %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }} hardware_type={{ item[1].hardware_type }}
{% endif %}
{% endfor %}

[{{ cluster_name }}-monitoringnodes]
{% for item in monitoringnodes|dictsort %}
{% if cluster_hardware_type %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }}
{% else %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }} hardware_type={{ item[1].hardware_type }}
{% endif %}
{% endfor %}

[{{ cluster_name }}-bootstraps]
{% for item in bootstraps|dictsort %}
{% if cluster_hardware_type %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }}
{% else %}
{{ item[0] }} ansible_ssh_host={{ item[1].ip_address }} ipmi_address={{ item[1].ipmi_address }} hardware_type={{ item[1].hardware_type }}
{% endif %}
{% endfor %}

[cluster:children]
headnodes
worknodes
ephemeral-worknodes
monitoringnodes

[bootstraps:children]
{{ cluster_name }}-bootstraps

[headnodes:children]
{{ cluster_name }}-headnodes

[worknodes:children]
{{ cluster_name }}-worknodes

[ephemeral-worknodes:children]
{{ cluster_name }}-ephemeral-worknodes

[monitoringnodes:children]
{{ cluster_name }}-monitoringnodes
"""


def render_inventory(path, ssh_user):
    f = open(path)
    cluster_yaml = f.read()
    f.close()
    cluster = yaml.safe_load(cluster_yaml)

    env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
    template = env.from_string(INVENTORY_TEMPLATE)

    hardware_types = set()
    bootstraps = {}
    headnodes = {}
    worknodes = {}
    eworknodes = {}
    monitoringnodes = {}
    cluster_hardware_type = None

    for node in cluster['nodes']:
        hardware_types.add(cluster['nodes'][node]['hardware_type'])
        if cluster['nodes'][node]['role'] == 'bootstrap':
            bootstraps[node] = cluster['nodes'][node]
        elif cluster['nodes'][node]['role'] == 'head':
            headnodes[node] = cluster['nodes'][node]
        elif cluster['nodes'][node]['role'] == 'work':
            worknodes[node] = cluster['nodes'][node]
        elif cluster['nodes'][node]['role'] == 'work-ephemeral':
            eworknodes[node] = cluster['nodes'][node]
        elif cluster['nodes'][node]['role'] == 'monitoring':
            monitoringnodes[node] = cluster['nodes'][node]

    # if None is detected as a hardware_type, the person needs to update
    # the YAML to actually have real hardware types
    if None in hardware_types:
        sys.exit("null is not a valid hardware type, please fix the YAML")
    # if only one hardware type was detected, we can avoid writing it out
    # for each node separately (Ansible doesn't care, but it reduces
    # visual clutter)
    if len(hardware_types) == 1:
        cluster_hardware_type = hardware_types.pop()

    return template.render(
        cluster_name=cluster['cluster_name'],
        cluster_hardware_type=cluster_hardware_type,
        cluster_ssh_user=ssh_user,
        bootstraps=bootstraps,
        headnodes=headnodes,
        worknodes=worknodes,
        eworknodes=eworknodes,
        monitoringnodes=monitoringnodes
    )


def main():
    parser = argparse.ArgumentParser(
        description='Takes cluster.yaml and emits an Ansible inventory.')
    parser.add_argument('path', help='path to cluster.yaml')
    parser.add_argument('-s', '--ssh_user',
        help='write this as ansible_ssh_user (default: %(default)s)',
        default='operations')
    args = parser.parse_args()

    if not os.path.exists(args.path) or not os.access(args.path, os.R_OK):
        sys.exit("ERROR: Unable to open %s" % args.path)

    print(render_inventory(args.path, args.ssh_user))


if __name__ == "__main__":
    main()
