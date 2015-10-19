Using Ansible
===

Introduction
---
The Ansible scripts in `bootstrap/ansible_scripts` provide a mechanism by which a hardware cluster can be bootstrapped. These scripts will also generally work on Vagrant-built virtualized nodes, with the exception of anything that uses IPMI or PXE boot. The Vagrant build path de-emphasizes the importance of the bootstrap node and uses it primarily as a Chef server, whereas the bootstrap node in a hardware cluster is of much greater importance, as it serves up packages and provides PXE booting services to the cluster. It is possible to manually construct a virtualized cluster where the cluster nodes can be PXE booted with Cobbler.

Known issues
---
* The environment validation playbook does not check everything it should.
* Playbooks that need to be written:
  * Full cluster power-down
  * Full cluster power-up via IPMI

cluster.yaml format
---
`cluster.yaml` is a YAML file that describes the hardware layout of your cluster. A sample layout:
```
cluster_name: TEST
nodes:
  fake-node-r06n01:
    domain: completelyfake.example
    hardware_type: Virtual
    ip_address: 131.81.229.220
    ipmi_address: 62.185.178.18
    mac_address: 21:b0:d5:9b:f8:3b
    role: bootstrap
  fake-node-r06n02:
    domain: completelyfake.example
    hardware_type: Virtual
    ip_address: 127.228.36.77
    ipmi_address: 218.161.198.210
    mac_address: 18:c2:93:42:a5:cd
    role: work
```
* Valid roles are: **bootstrap**, **head**, **work**, **work-ephemeral**, or **reserved**.
* The MAC address is used by Cobbler for PXE booting.
* The hardware type is interpolated into the string **BCPC-Hardware-[hardware_type]** when selecting a role to represent the node's hardware type.

Cluster bootstrap in a nutshell
---
* install Ansible on the control node (1.9.4 recommended)
* prepare `chef-bcpc-prop` with a filled-out `cluster.txt` (see `docs/cluster.txt.example` for the format)
* prepare the apt mirror on the control node
  * see `docs/example_apt_mirror_config.list` for a recommended apt-mirror configuration
  * total space take will be around 130GB for all mirrors; keep this in mind if syncing the mirrors into a virtualized bootstrap node
* configure a node to act as the bootstrap node with three block devices
  * `sda` is the root volume
  * `sdb` is mounted at `/mnt` (scratch space)
  * `sdc` is mounted at `/bcpc` (contains everything used by the bootstrap process)
* manually install Ubuntu 14.04 LTS on the bootstrap node
  * it is recommended that you create a user named **ubuntu** during setup, as this user will be needed to create the **operations** user and will then be disabled by `tasks-create-bootstrap-users.yml`
* configure your cluster's hardware layout in `cluster.txt` or `cluster.yaml`
  * if you have an existing `cluster.txt`, it can be converted to `cluster.yaml` with `bootstrap/ansible_scripts/scripts/cluster_manifest_converter.py`
  * if you convert, you will need to fill out the hardware type for each node (`cluster.txt` does not carry this information)
* configure your cluster inventory in `bootstrap/ansible_scripts/inventory-clustername`, using `inventory.template` as a reference
  * if you have filled out `cluster.yaml`, use `bootstrap/ansible_scripts/scripts/cluster_yaml_to_inventory.py` to automatically generate the Ansible inventory file for the cluster
  * in order to make it easy to work with cluster nodes after the operations keypair is installed, it is recommended that you define `ansible_ssh_user: operations` in the inventory file and override it only when running the playbooks that create the **operations** user
* configure your global group_vars in `bootstrap/ansible_scripts/group_vars/all`, using `all.template` as a reference
* configure your cluster group_vars in `bootstrap/ansible_scripts/group_vars/clustername`, using `cluster.template` as a reference
  * **NOTE**: variables defined in group_vars can be moved between `all` and individual clusters as desired
  * for example, you may wish to use a different IPMI password/username per cluster, or the same operations keypair for all clusters
* **NOTE**: all playbooks should be executed from `bootstrap/ansible_scripts` due to Ansible path layout requirements
* execute `create-operations-user-on-bootstrap.yml`
```
ansible-playbook -k -K -e 'ansible_ssh_user=ubuntu' -i inventory-file bootstrap_deployment/create-operations-user-on-bootstrap.yml
```
* execute `converge-bootstrap.yml`
```
ansible-playbook -i inventory-file bootstrap_deployment/converge-bootstrap.yml
```
  * this playbook calls various tasks in the `bootstrap_deployment` and `software_deployment` directories
  * this playbook is very complex and does a lot of things that can break, but it is safe to run from the beginning repeatedly if you need to fix things in-flight
  * as part of package configuration, this will mirror the entire apt repository over to the bootstrap node, which can take several hours
  * if running this on a virtualized bootstrap node, **ensure that you have available space for 2 full copies of the apt mirror**, as it will all be rsynced into the VM
* execute `enroll-all-nodes-in-cobbler.yml`
```
ansible-playbook -i inventory-file bootstrap_deployment/enroll-all-nodes-in-cobbler.yml
```
  * this playbook executes `cluster-enroll-cobbler.sh` from the root of the repository on the bootstrap node, which reads `cluster.txt` (has not yet been updated to use `cluster.yaml`) and enrolls the requested nodes or updates them to match `cluster.txt`
  * if you have not filled out `cluster.txt`, this playbook will execute but the calls to the script will not actually do anything
  * `cluster.txt` is typically injected into the bootstrap node via the `chef-bcpc-prop` repo, which allows inserting and overwriting arbitrary files in the `chef-bcpc` repository
  * verify the Cobbler enrollments with `sudo cobbler system list`
* reboot cluster nodes and wait for them to be PXE booted and have the OS installed
* create **operations** user on newly booted nodes
```
ansible-playbook -k -K -e 'ansible_ssh_user=ubuntu' -i inventory-file cluster_management/create-operations-user-everywhere.yml
```
  * password for the **ubuntu** user can be obtained from the data bag on the bootstrap node with `knife data bag show configs ENVIRONMENT`
  * **ubuntu** user on cluster nodes is not deleted, but using the **operations** user for access is recommended
* enroll nodes in Chef using `software_deployment/enroll-node-in-chef.yml`
```
ansible-playbook -i inventory-file -e target=xxxx software_deployment/enroll-node-in-chef.yml
```
  * `target=xxxx` is an Ansible host pattern, like **headnodes**, **worknodes:ephemeral-worknodes**, or a specific node name
* assign a node's hardware role and cluster role using `software_deployment/assign-target-roles.yml`
  * this playbook will work out the appropriate role based on the hostgroup the node is in, so if a node is in multiple hostgroups Weird Things will happen (i.e., don't put a node in both **[xxxx:headnodes]** and **[xxxx:worknodes]** in the inventory)
  * **NOTE**: do not set the head node role on more than one uncheffed head node at a time, because this will cause failures in Chef resources that use node searches
  * after adding a new head node, it is advisable to rechef all other head nodes after initially cheffing the new head node so that items like database connection counts can be updated (if you see weird failures when cheffing a second head node, database connection count issues are probably why and recheffing the first head node will correct it)
* if reinstalling an existing hardware cluster, use `hardware_deployment/erase-data-disks.yml` with the **target** option to destroy existing Ceph/LVM partition tables and structures to avoid problems when recheffing
  * this playbook is obviously extremely dangerous and will bail if it detects Ceph or nova-compute processes on any target, but **BEWARE**
* chef the node using `software_deployment/chef-target.yml`
```
ansible-playbook -i inventory-file -e target=xxxx software_deployment/chef-target.yml
```
