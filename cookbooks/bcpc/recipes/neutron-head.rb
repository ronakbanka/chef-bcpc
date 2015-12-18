#
# Cookbook Name:: bcpc
# Recipe:: neutron-head
#
# Copyright 2015, Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

include_recipe "bcpc::neutron-common"

%w{neutron-server neutron-metadata-agent}.each do |pkg|
  package pkg do
    action :upgrade
    options "-o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold'"
  end

  service pkg do
    action [:enable, :start]
    subscribes :restart, "template[/etc/neutron/neutron.conf]", :delayed
    subscribes :restart, "template[/etc/neutron/plugins/ml2/ml2_conf.ini]", :delayed
    subscribes :restart, "template[/etc/neutron/policy.json]", :delayed
  end
end

ruby_block "neutron-database-creation" do
  block do
    %x[ export MYSQL_PWD=#{get_config('mysql-root-password')};
        mysql -uroot -e "CREATE DATABASE #{node['bcpc']['dbname']['neutron']};"
        mysql -uroot -e "GRANT ALL ON #{node['bcpc']['dbname']['neutron']}.* TO '#{get_config('mysql-neutron-user')}'@'%' IDENTIFIED BY '#{get_config('mysql-neutron-password')}';"
        mysql -uroot -e "GRANT ALL ON #{node['bcpc']['dbname']['neutron']}.* TO '#{get_config('mysql-neutron-user')}'@'localhost' IDENTIFIED BY '#{get_config('mysql-neutron-password')}';"
        mysql -uroot -e "FLUSH PRIVILEGES;"
    ]
    self.notifies :run, "bash[neutron-database-sync]", :immediately
    self.resolve_notification_references
  end
  not_if { system "MYSQL_PWD=#{get_config('mysql-root-password')} mysql -uroot -e 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = \"#{node['bcpc']['dbname']['neutron']}\"'|grep \"#{node['bcpc']['dbname']['neutron']}\" >/dev/null" }
end

bash "neutron-database-sync" do
  action :nothing
  user "root"
  code "neutron-db-manage upgrade heads"
end

include_recipe "bcpc::neutron-work"
