#
# Cookbook Name:: bcpc
# Recipe:: neutron-common
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

include_recipe "bcpc::openstack"

ruby_block "initialize-neutron-config" do
  block do
    make_config('mysql-neutron-user', "neutron")
    make_config('mysql-neutron-password', secure_password)
  end
end

package 'neutron-common' do
  action :upgrade
  options "-o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold'"
end

%w{/etc/neutron /etc/neutron/plugins/ml2 /etc/neutron/plugins/openvswitch}.each do |d|
  directory d do
    owner 'neutron'
    group 'neutron'
    mode 00700
    recursive true
  end
end

template '/etc/neutron/neutron.conf' do
  source 'neutron.conf.erb'
  owner 'neutron'
  group 'neutron'
  mode 00600
  variables(
    lazy {
      {:servers => get_head_nodes}
    }
  )
end

template '/etc/neutron/plugins/ml2/ml2_conf.ini' do
  source 'neutron.ml2_conf.ini.erb'
  owner 'neutron'
  group 'neutron'
  mode 00600
end

link '/etc/neutron/plugin.ini' do
  to '/etc/neutron/plugins/ml2/ml2_conf.ini'
end

template "/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini" do
  source "neutron.ovs_neutron_plugin.ini.erb"
  owner "neutron"
  group "neutron"
  mode 00600
end
