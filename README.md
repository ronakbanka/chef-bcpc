Overview
========
This is a set of [Chef](https://github.com/opscode/chef) cookbooks to bring up
an instance of an [OpenStack](http://www.openstack.org/)-based cluster of head
and worker nodes.  In addition to hosting virtual machines, there are a number
of additional services provided with these cookbooks - such as distributed
storage, DNS, log aggregation/search, and monitoring - see below for a partial
list of services provided by these cookbooks.

Each head node runs all of the core services in a highly-available manner with
no restriction upon how many head nodes there are.  The cluster is deemed
operational as long as 50%+1 of the head nodes are online.  Otherwise, a
network partition may occur with a split-brain scenario.  In practice,
we currently recommend roughly one head node per rack.

Each worker node runs the relevant services (nova-compute, Ceph OSDs, etc.).
There is no limitation on the number of worker nodes.  In practice, we
currently recommend that the cluster should not grow to more than 200 worker
nodes.

Setup
=====
To get going in a hurry, we recommend the Vagrant mechanism for building your cluster. Please read the [Vagrant Bootstrap Guide](https://github.com/bloomberg/chef-bcpc/blob/master/docs/building_with_vagrant.md) for information on getting BCPC set up locally with Vagrant.

If you are interested in building your cluster the hard way without Vagrant, there are Ansible scripts in `bootstrap/ansible_scripts` for creating a hardware cluster that can be applied to a virtualized cluster (manual work will be required). The Ansible scripts are documented at [Using Ansible](https://github.com/bloomberg/chef-bcpc/blob/master/docs/using_ansible.md).

BCPC Services
-------------
BCPC is built using the following open-source software:

 - [Apache HTTP Server](http://httpd.apache.org/)
 - [Ceph](http://ceph.com/)
 - [Chef](http://www.opscode.com/chef/)
 - [Cobbler](http://www.cobblerd.org/)
 - [Diamond](https://github.com/BrightcoveOS/Diamond)
 - [ElasticSearch](http://www.elasticsearch.org/)
 - [Etherboot](http://etherboot.org/)
 - [Fluentd](http://fluentd.org/)
 - [Graphite](http://graphite.readthedocs.org/en/latest/)
 - [HAProxy](http://haproxy.1wt.eu/)
 - [Keepalived](http://www.keepalived.org/)
 - [Kibana](http://kibana.org/)
 - [Memcached](http://memcached.org)
 - [OpenStack](http://www.openstack.org/)
 - [Percona XtraDB Cluster](http://www.percona.com/software/percona-xtradb-cluster)
 - [PowerDNS](https://www.powerdns.com/)
 - [RabbitMQ](http://www.rabbitmq.com/)
 - [Ubuntu](http://www.ubuntu.com/)
 - [Vagrant](http://www.vagrantup.com/) - 1.7.4 or better recommended
 - [VirtualBox](https://www.virtualbox.org/) - 5.0.0 or better recommended
 - [Zabbix](http://www.zabbix.com/)

Thanks to all of these communities for producing this software!
