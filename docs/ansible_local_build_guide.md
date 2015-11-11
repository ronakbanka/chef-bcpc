Ansible local build guide
===
This process is designed to simulate an actual hardware build-out as closely as possible. To that end, it sacrifices speed and convenience for correctness. There are a number of manual steps, and there are some steps that are not necessary on actual hardware builds in order to trick certain parts of the software stack (mostly having to do with the networking layout). Where present, these steps will be indicated.

You **must** have a complete local copy of all packages repositories and at least 250GB of disk space free in order to support the simulation cluster, as the entire package repository will be rsynced into the virtualized bootstrap node.

Minimum Prerequisites
---------------------
* OS X or Linux
* Processor that supports VT-x virtualization extensions
* 16 GB of memory
* 250 GB of free disk space
* Ansible 1.9.4 or better
* VirtualBox 4.3 or better (5.0+ recommended) ([https://www.virtualbox.org](https://www.virtualbox.org))
* Git, curl, rsync, ssh, pcregrep
* sshpass if using Linux

Preparation
---
* Create a staging location on your build host (e.g., `$HOME/bcpc-deployment`). This directory is useful for storing various files used by the build process, as well as a virtualenv for Ansible.
* Copy `bootstrap/ansible_scripts/group_vars/vars.template` to `Test-Laptop-Ansible` within that same directory. This file will be referred to as the **group variables** file.
* Create a `git-staging` directory underneath this directory. Set the value of `controlnode_git_staging_dir` in the group variables to this value.
* Create a `bootstrap-files` directory underneath this directory. Set the value of `controlnode_files_dir` in the group variables to this value.
* Copy the contents of your BCPC bootstrap cache (by default, `$HOME/.bcpc-cache`) to `bootstrap-files/master`. Symlinks will **not** work. If you do not have a local BCPC cache, run `BOOTSTRAP_CACHE_DIR=$HOME/.bcpc-cache REPO_ROOT=$(git rev-parse --show-toplevel) bootstrap/shared/shared_prereqs.sh` from the root of the repository to populate the cache.
* Locate the root of your apt mirror. Set the value of `controlnode_apt_mirror_dir` in the group variables to this value.
* Generate an SSH key pair in your staging directory with `ssh-keygen -f test-laptop-ansible`. Set the value of `ansible_ssh_private_key_file` in the group variables to the path to the private key. Set the value of `operations_key` to the public key itself (copy and paste it in there, don't provide the path).
* Uncomment `chef_bcpc_deploy_from_dir` and set it to the path of the root of the **chef-bcpc** repository.
* Review the group variables for any additional settings you may wish to or need to change.
* Install **virtualenv** via `pip install virtualenv` or operating system packages so that you may install Ansible and its support packages without interfering with Python on your system.
* Create a virtualenv in the staging directory with `virtualenv path/to/staging-dir` (if you are in the directory, `virtualenv .` will suffice). The virtualenv must be using Python 2.x and not Python 3.x because of Ansible restrictions, so if the virtualenv is set up with the wrong Python interpreter, please recreate it with the `-p` setting.
* Activate the virtualenv from within the staging directory with `source bin/activate`.
* Install the most current version of Ansible available on the build host with `pip install ansible` (Python 2.x required). You will also need a handful of additional Python modules from pip:
  * yaml
  * Jinja2
  * MarkupSafe
* Download an Ubuntu server ISO from [http://www.ubuntu.com/download/server] to boot the bootstrap node from.

Creating VMs
---
* Run `bootstrap/ansible_scripts/scripts/spawn_local_vms.sh` to build the VMs in VirtualBox (existing BCPC VMs will be deleted without mercy). This script will output the MAC addresses of the first network interface of each node.
* Create `cluster.yml` in your staging directory, using `bootstrap/ansible_scripts/ansible-cluster.yml.example` as a model. For a local build, you should only need to replace the sample MAC addresses with the real ones.
* Convert `cluster.yml` to `cluster.txt` with `bootstrap/ansible_scripts/scripts/cluster_manifest_converter.py -t cluster.yml Test-Laptop-Ansible > cluster.txt`.
* Copy `cluster.txt` to the root of the `chef-bcpc` repository (a number of legacy scripts that have not yet been updated to use `cluster.yml` expect `cluster.txt` to be located here).  

Installing the OS on the bootstrap node
---
***NOTE: this process is somewhat involved and annoying. It will be replaced with a Packer image that incorporates everything automatically in the near future.***

* Attach the ISO to the DVD drive of the **bcpc-bootstrap** node.
* Boot the bootstrap node and install the operating system.
* Select **eth0** as the primary network interface (additional interfaces will be configured manually after installation).
  * **eth0** is the VirtualBox NAT interface that allows the bootstrap node to access the Internet.
  * In actual hardware builds, an Internet connection is not necessary or expected to be present; this interface's presence is a concession to convenience so that DNS works properly, otherwise every SSH connection will take ~10 seconds due to reverse DNS lookup timeouts.
  * If you have a local DNS server on your build host, you can remove this interface from the VM; remember to update the Chef environment and change the value of the **bcpc.bootstrap.pxe_interface** key to move it up one spot.
* Enter **bcpc-bootstrap** as the hostname.
* Create an account named **ubuntu** (password can be whatever you like).
* Partition `/dev/sda` using the **Guided - use entire disk** method. The other disks do not need to be partitioned or formatted at this time.
* Software selection:
  * Select **OpenSSH server**.
  * **If you wish to mount the apt mirror via VirtualBox shared folders**, you must also do **Manual package selection**:
    * Check **Manual package selection** and continue.
    * When **aptitude** launches, press the `/` key and enter `build-essential`, then press Return.
    * Press the `+` key to add the **build-essential** package to the list of packages to be installed (the text will change to green).
    * Press the `G` key twice to begin installing packages from Aptitude. (Some packages will fail the configuration step, but this is okay).
    * After package installation is complete, press Return, then quit Aptitude with the `Q` key.
* GRUB can go in the MBR.

Manually configuring bootstrap node network
---
* **Manual network reconfiguration required!**
* You must manually configure **eth1** through **eth3** on the bootstrap node via the VirtualBox console before you can SSH in.
* Modify `/etc/network/interfaces` as follows:
```
auto eth0 eth1 eth2 eth3
iface eth0 inet dhcp
iface eth1 inet static
	address 10.0.100.3
	netmask 255.255.255.0
	network 10.0.100.0
	broadcast 10.0.100.255
iface eth2 inet static
	address 172.16.100.3
	netmask 255.255.255.0
	network 172.16.100.0
	broadcast 172.16.100.255
iface eth3 inet static
	address 192.168.100.3
	netmask 255.255.255.0
	network 192.168.100.0
	broadcast 192.168.100.255
```
* After configuring, bring up each interface with `ifup` and test that you can ping **.2** for each network (e.g., **10.0.100.2**, which is your build host).
* Test SSHing to the node from the build host and verify everything appears to be in order.

The rest
---
Have a look at **ansible_cluster_convergence.md** for information on converging nodes and getting the full cluster up and running.
