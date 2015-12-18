#
# Cookbook Name:: bcpc
# Recipe:: neutron-work
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

%w{neutron-dhcp-agent neutron-plugin-ml2 neutron-plugin-openvswitch-agent}.each do |pkg|
  package pkg do
    action :upgrade
    options "-o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold'"
  end
end

%w{neutron-dhcp-agent neutron-plugin-openvswitch-agent}.each do |svc|
  service svc do
    action [:enable, :start]
  end
end
