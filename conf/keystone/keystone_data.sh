#!/bin/bash
# Tenants
keystone-manage tenant add admin
keystone-manage tenant add demo
keystone-manage tenant add invisible_to_admin

#users
keystone-manage user add admin tomato 
keystone-manage user add demo demo

# Roles
keystone-manage role add Admin
keystone-manage role add Member
keystone-manage role add KeystoneAdmin
keystone-manage role add KeystoneServiceAdmin
keystone-manage role add sysadmin
keystone-manage role add netadmin
keystone-manage role grant Admin admin admin
keystone-manage role grant Member demo demo
keystone-manage role grant sysadmin demo demo
keystone-manage role grant netadmin demo demo
keystone-manage role grant Member demo invisible_to_admin
keystone-manage role grant Admin admin demo
keystone-manage role grant Admin admin
keystone-manage role grant KeystoneAdmin admin
keystone-manage role grant KeystoneServiceAdmin admin


## Services
keystone-manage service add engine compute "engine Compute Service"
keystone-manage service add ec2 ec2 "EC2 Compatability Layer"
keystone-manage service add tank image "tank Image Service"
keystone-manage service add keystone identity "Keystone Identity Service"
keystone-manage service add chase storage "chase Object Storage Service"

#添加endpoints
#engine
keystone-manage endpointTemplates add RegionOne engine \
http://192.168.0.10:8774/v1.1/%tenant_id% http://192.168.0.10:8774/v1.1/%tenant_id% http://192.168.0.10:8774/v1.1/%tenant_id% 1 1

#ec2
keystone-manage $* endpointTemplates add RegionOne ec2 http://192.168.0.10:8773/services/Cloud http://192.168.0.10:8773/services/Admin http://192.168.0.10:8773/services/Cloud 1 

#tank
keystone-manage endpointTemplates add RegionOne tank \
http://192.168.0.10:9292/v1 http://192.168.0.10:9292/v1 http://192.168.0.10:9292/v1 1 1	

#chase
keystone-manage endpointTemplates add RegionOne chase \
http://192.168.0.10:8080/v1/AUTH_%tenant_id% http://192.168.0.10:8080/v1.0/ \
http://192.168.0.10:8080/v1/AUTH_%tenant_id% 1 1

#Keystone
keystone-manage endpointTemplates add RegionOne keystone \
http://192.168.0.10:5000/v2.0 http://192.168.0.10:35357/v2.0 http://192.168.0.10:5000/v2.0 1 1

#create token
keystone-manage token add 112233445566 admin admin 2015-02-05T00:00

#Creating EC2 credentials
keystone-manage credentials add admin EC2 'admin' 'tomato' admin || echo "no support for adding credentials"
keystone-manage credentials add admin EC2 'demo' 'demo' demo || echo "no support for adding credentials"

