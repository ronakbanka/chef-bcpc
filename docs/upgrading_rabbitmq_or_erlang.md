Upgrading RabbitMQ or Erlang
===

If upgrading RabbitMQ or Erlang in a multi-head node cluster, please read the guide below.

Per the [RabbitMQ guide to upgrading](https://www.rabbitmq.com/clustering.html#upgrading), a single cluster can run with different minor RabbitMQ versions, but all RabbitMQ nodes must be using the same Erlang version.

If upgrading between minor RabbitMQ versions, things should continue to operate without drama throughout. Using `hup_openstack` to restart services on each head node in turn may help clear up any lingering issues.

If upgrading Erlang:

1. Stop RabbitMQ on all nodes but one with `sudo service rabbitmq-server stop` (ideally keep the one that is holding the stats role running).
2. Upgrade Erlang on the running node and restart RabbitMQ.
3. Verify that the node has restarted properly.
4. Upgrade each other RabbitMQ node in turn.

If upgrading major RabbitMQ versions:

1. Read RabbitMQ's release notes carefully for any issues that may be encountered in upgrading from one major version to another.
2. Follow the steps for an Erlang upgrade, stopping all nodes but one and gradually reintroducing upgraded nodes into the cluster.
