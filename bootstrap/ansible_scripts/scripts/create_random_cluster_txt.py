#!/usr/bin/env python

"""
This script will randomly generate a cluster.txt in the appropriate format
for testing purposes (so that scripts that work with it can be validated
without needing to be tested on actual cluster.txt files that may contain
privileged information).

cluster.txt layout:

column 1: node name
column 2: MAC address of first network interface
column 3: IP address of OS management network
column 4: IPMI/LOM IP address
column 5: domain
column 6: role (bootstrap/head/work/work-ephemeral)
"""

import random


def generate_random_cluster_list(
        node_domain="completelyfake.example",
        node_prefix="fake-node",
        nodes=100,
        rack_step=16):
    """
    Emits a list of lists that can be turned into a real cluster.txt
    by joining the lists with whitespace separators.
    """
    possible_roles = [
        'bootstrap',
        'head',
        'work',
        'work-ephemeral',
        'monitoring',
        'reserved']

    cluster_list = []

    rack_number = random.randint(1, 12)
    node_number = 1

    head_node_count = 0  # maximum of 5
    monitoring_node_count = 0  # maximum of 3

    for n in range(nodes):
        node_name = "%s-r%02dn%02d" % (node_prefix, rack_number, node_number)
        mac_address = ":".join(
            ["%02x" % random.randint(0, 255) for i in range(0, 6)])
        ip_address = ".".join(
            [str(random.randint(1, 255)) for i in range(0, 4)])
        ipmi_address = ".".join(
            [str(random.randint(1, 255)) for i in range(0, 4)])
        role = random.choice(possible_roles)

        # hack to avoid multiple bootstrap nodes or too many head nodes
        if role == 'bootstrap':
            possible_roles.remove('bootstrap')
        if role == 'head':
            head_node_count += 1
        if head_node_count >= 5:
            if 'head' in possible_roles:
                possible_roles.remove('head')
        if role == 'monitoring':
            monitoring_node_count += 1
        if monitoring_node_count >= 3:
            if 'monitoring' in possible_roles:
                possible_roles.remove('monitoring')

        cluster_list.append([node_name,
                             mac_address,
                             ip_address,
                             ipmi_address,
                             node_domain,
                             role])

        node_number += 1
        if node_number > rack_step:
            node_number = 1
            rack_number += 1

    return cluster_list


def main():
    for line in generate_random_cluster_list():
        print(" ".join(line))
    print("end")

if __name__ == '__main__':
    main()
