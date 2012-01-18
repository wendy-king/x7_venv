==============================================================
Instructions for a Multiple Server Chase Installation (Ubuntu)
==============================================================

Prerequisites
-------------
* Ubuntu Server 10.04 LTS installation media

.. note:
    Chase can run with other distros, but for this document we will focus
    on installing on Ubuntu Server, ypmv (your packaging may vary).

Basic architecture and terms
----------------------------
- *node* - a host machine running one or more Chase services
- *Proxy node* - node that runs Proxy services; also runs TempAuth
- *Storage node* - node that runs Account, Container, and Object services
- *ring* - a set of mappings of Chase data to physical devices

This document shows a cluster using the following types of nodes:

- one Proxy node

  - Runs the chase-proxy-server processes which proxy requests to the
    appropriate Storage nodes. The proxy server will also contain
    the TempAuth service as WSGI middleware.

- five Storage nodes

  - Runs the chase-account-server, chase-container-server, and 
    chase-object-server processes which control storage of the account
    databases, the container databases, as well as the actual stored
    objects.
    
.. note::
    Fewer Storage nodes can be used initially, but a minimum of 5 is
    recommended for a production cluster.

This document describes each Storage node as a separate zone in the ring.
It is recommended to have a minimum of 5 zones. A zone is a group of nodes
that is as isolated as possible from other nodes (separate servers, network,
power, even geography). The ring guarantees that every replica is stored
in a separate zone.  For more information about the ring and zones, see: :doc:`The Rings <overview_ring>`.

To increase reliability, you may want to add additional Proxy servers for performance which is described in :ref:`add-proxy-server`.

Network Setup Notes
-------------------

This document refers to two networks.  An external network for connecting to the Proxy server, and a storage network that is not accessibile from outside the cluster, to which all of the nodes are connected.  All of the Chase services, as well as the rsync daemon on the Storage nodes are configured to listen on their STORAGE_LOCAL_NET IP addresses.

.. note::
    Run all commands as the root user

General OS configuration and partitioning for each node
-------------------------------------------------------

#. Install the baseline Ubuntu Server 10.04 LTS on all nodes.

#. Install common Chase software prereqs::

        apt-get install python-software-properties
        add-apt-repository ppa:chase-core/release
        apt-get update
        apt-get install chase openssh-server

#. Create and populate configuration directories::

        mkdir -p /etc/chase
        chown -R chase:chase /etc/chase/

#. On the first node only, create /etc/chase/chase.conf::

        cat >/etc/chase/chase.conf <<EOF
        [chase-hash]
        # random unique string that can never change (DO NOT LOSE)
        chase_hash_path_suffix = `od -t x8 -N 8 -A n </dev/random`
        EOF

#. On the second and subsequent nodes: Copy that file over. It must be the same on every node in the cluster!::

        scp firstnode.example.com:/etc/chase/chase.conf /etc/chase/  

#. Publish the local network IP address for use by scripts found later in this documentation::

        export STORAGE_LOCAL_NET_IP=10.1.2.3
        export PROXY_LOCAL_NET_IP=10.1.2.4

.. note::
    The random string of text in /etc/chase/chase.conf is 
    used as a salt when hashing to determine mappings in the ring. 

.. _config-proxy:

Configure the Proxy node
------------------------

.. note::
    It is assumed that all commands are run as the root user

#. Install chase-proxy service::

        apt-get install chase-proxy memcached

#. Create self-signed cert for SSL::

        cd /etc/chase
        openssl req -new -x509 -nodes -out cert.crt -keyout cert.key

.. note::
	If you don't create the cert files, Chase silently uses http internally rather than https. This document assumes that you have created
	these certs, so if you're following along step-by-step, create them.

#. Modify memcached to listen on the default interfaces. Preferably this should be on a local, non-public network. Edit the IP address in /etc/memcached.conf, for example::

        perl -pi -e "s/-l 127.0.0.1/-l $PROXY_LOCAL_NET_IP/" /etc/memcached.conf

#. Restart the memcached server::

        service memcached restart

#. Create /etc/chase/proxy-server.conf::

        cat >/etc/chase/proxy-server.conf <<EOF
        [DEFAULT]
        cert_file = /etc/chase/cert.crt
        key_file = /etc/chase/cert.key
        bind_port = 8080
        workers = 8
        user = chase
        
        [pipeline:main]
        pipeline = healthcheck cache tempauth proxy-server
        
        [app:proxy-server]
        use = egg:chase#proxy
        allow_account_management = true
        
        [filter:tempauth]
        use = egg:chase#tempauth
        user_system_root = testpass .admin https://$PROXY_LOCAL_NET_IP:8080/v1/AUTH_system
        
        [filter:healthcheck]
        use = egg:chase#healthcheck
        
        [filter:cache]
        use = egg:chase#memcache
        memcache_servers = $PROXY_LOCAL_NET_IP:11211
        EOF

   .. note::

    If you run multiple memcache servers, put the multiple IP:port listings    
    in the [filter:cache] section of the proxy-server.conf file like:
    `10.1.2.3:11211,10.1.2.4:11211`. Only the proxy server uses memcache.

#. Create the account, container and object rings. The builder command is basically creating a builder file with a few parameters. The parameter with the value of 18 represents 2 ^ 18th, the value that the partition will be sized to. Set this "partition power" value based on the total amount of storage you expect your entire ring to use. The value of 3 represents the number of replicas of each object, with the last value being the number of hours to restrict moving a partition more than once.

::

    cd /etc/chase
    chase-ring-builder account.builder create 18 3 1
    chase-ring-builder container.builder create 18 3 1
    chase-ring-builder object.builder create 18 3 1
    
   .. note::

    For more information on building rings, see :doc:`overview_ring`.
        
#. For every storage device in /srv/node on each node add entries to each ring::

    export ZONE=                    # set the zone number for that storage device
    export STORAGE_LOCAL_NET_IP=    # and the IP address
    export WEIGHT=100               # relative weight (higher for bigger/faster disks)
    export DEVICE=sdb1
    chase-ring-builder account.builder add z$ZONE-$STORAGE_LOCAL_NET_IP:6002/$DEVICE $WEIGHT
    chase-ring-builder container.builder add z$ZONE-$STORAGE_LOCAL_NET_IP:6001/$DEVICE $WEIGHT
    chase-ring-builder object.builder add z$ZONE-$STORAGE_LOCAL_NET_IP:6000/$DEVICE $WEIGHT

   .. note::
    Assuming there are 5 zones with 1 node per zone, ZONE should start at
    1 and increment by one for each additional node.

#. Verify the ring contents for each ring::

    chase-ring-builder account.builder
    chase-ring-builder container.builder
    chase-ring-builder object.builder
    
#. Rebalance the rings::

    chase-ring-builder account.builder rebalance
    chase-ring-builder container.builder rebalance
    chase-ring-builder object.builder rebalance

   .. note::
    Rebalancing rings can take some time.

#. Copy the account.ring.gz, container.ring.gz, and object.ring.gz files
   to each of the Proxy and Storage nodes in /etc/chase.

#. Make sure all the config files are owned by the chase user::

        chown -R chase:chase /etc/chase

#. Start Proxy services::

        chase-init proxy start


Configure the Storage nodes
---------------------------

..  note::
    Chase *should* work on any modern filesystem that supports
    Extended Attributes (XATTRS). We currently recommend XFS as it
    demonstrated the best overall performance for the chase use case after
    considerable testing and benchmarking at Rackspace. It is also the
    only filesystem that has been thoroughly tested. These instructions 
    assume that you are going to devote /dev/sdb1 to an XFS filesystem.

#. Install Storage node packages::

        apt-get install chase-account chase-container chase-object xfsprogs

#. For every device on the node, setup the XFS volume (/dev/sdb is used
   as an example)::

        fdisk /dev/sdb  (set up a single partition)
        mkfs.xfs -i size=1024 /dev/sdb1
        echo "/dev/sdb1 /srv/node/sdb1 xfs noatime,nodiratime,nobarrier,logbufs=8 0 0" >> /etc/fstab
        mkdir -p /srv/node/sdb1
        mount /srv/node/sdb1
        chown -R chase:chase /srv/node

#. Create /etc/rsyncd.conf::

        cat >/etc/rsyncd.conf <<EOF
        uid = chase
        gid = chase
        log file = /var/log/rsyncd.log
        pid file = /var/run/rsyncd.pid
        address = $STORAGE_LOCAL_NET_IP
        
        [account]
        max connections = 2
        path = /srv/node/
        read only = false
        lock file = /var/lock/account.lock
        
        [container]
        max connections = 2
        path = /srv/node/
        read only = false
        lock file = /var/lock/container.lock
        
        [object]
        max connections = 2
        path = /srv/node/
        read only = false
        lock file = /var/lock/object.lock
        EOF

#. Edit the RSYNC_ENABLE= line in /etc/default/rsync::

        perl -pi -e 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/' /etc/default/rsync

#. Start rsync daemon::

        service rsync start

   ..  note::
    The rsync daemon requires no authentication, so it should be run on
    a local, private network.

#. Create /etc/chase/account-server.conf::

        cat >/etc/chase/account-server.conf <<EOF
        [DEFAULT]
        bind_ip = $STORAGE_LOCAL_NET_IP
        workers = 2
        
        [pipeline:main]
        pipeline = account-server
        
        [app:account-server]
        use = egg:chase#account
        
        [account-replicator]

        [account-auditor]
        
        [account-reaper]
        EOF

#. Create /etc/chase/container-server.conf::

        cat >/etc/chase/container-server.conf <<EOF
        [DEFAULT]
        bind_ip = $STORAGE_LOCAL_NET_IP
        workers = 2
        
        [pipeline:main]
        pipeline = container-server
        
        [app:container-server]
        use = egg:chase#container
        
        [container-replicator]
        
        [container-updater]
        
        [container-auditor]
        EOF

#. Create /etc/chase/object-server.conf::

        cat >/etc/chase/object-server.conf <<EOF
        [DEFAULT]
        bind_ip = $STORAGE_LOCAL_NET_IP
        workers = 2
        
        [pipeline:main]
        pipeline = object-server
        
        [app:object-server]
        use = egg:chase#object
        
        [object-replicator]
        
        [object-updater]
        
        [object-auditor]
        EOF

#. Start the storage services. If you use this command, it will try to start every
service for which a configuration file exists, and throw a warning for any
configuration files which don't exist::

         chase-init all start

Or, if you want to start them one at a time, run them as below. Note that if the
server program in question generates any output on its stdout or stderr, chase-init
has already redirected the command's output to /dev/null. If you encounter any
difficulty, stop the server and run it by hand from the command line. Any server
may be started using "chase-$SERVER-$SERVICE /etc/chase/$SERVER-config", where
$SERVER might be object, continer, or account, and $SERVICE might be server,
replicator, updater, or auditor.::

         chase-init object-server start
         chase-init object-replicator start
         chase-init object-updater start
         chase-init object-auditor start
         chase-init container-server start
         chase-init container-replicator start
         chase-init container-updater start
         chase-init container-auditor start
         chase-init account-server start
         chase-init account-replicator start
         chase-init account-auditor start

Create Chase admin account and test
-----------------------------------

You run these commands from the Proxy node.

#. Get an X-Storage-Url and X-Auth-Token::

        curl -k -v -H 'X-Storage-User: system:root' -H 'X-Storage-Pass: testpass' https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0

#. Check that you can HEAD the account::

        curl -k -v -H 'X-Auth-Token: <token-from-x-auth-token-above>' <url-from-x-storage-url-above>

#. Check that ``chase`` works  (at this point, expect zero containers, zero objects, and zero bytes)::

        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass stat

#. Use ``chase`` to upload a few files named 'bigfile[1-2].tgz' to a container named 'myfiles'::

        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass upload myfiles bigfile1.tgz
        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass upload myfiles bigfile2.tgz

#. Use ``chase`` to download all files from the 'myfiles' container::

        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass download myfiles

#. Use ``chase`` to save a backup of your builder files to a container named 'builders'. Very important not to lose your builders!::

        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass upload builders /etc/chase/*.builder

#. Use ``chase`` to list your containers::

        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass list

#. Use ``chase`` to list the contents of your 'builders' container::

        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass list builders

#. Use ``chase`` to download all files from the 'builders' container::

        chase -A https://$PROXY_LOCAL_NET_IP:8080/auth/v1.0 -U system:root -K testpass download builders

.. _add-proxy-server:

Adding a Proxy Server
---------------------

For reliability's sake you may want to have more than one proxy server. You can set up the additional proxy node in the same manner that you set up the first proxy node but with additional configuration steps. 

Once you have more than two proxies, you also want to load balance between the two, which means your storage endpoint also changes. You can select from different strategies for load balancing. For example, you could use round robin dns, or an actual load balancer (like pound) in front of the two proxies, and point your storage url to the load balancer.

See :ref:`config-proxy` for the initial setup, and then follow these additional steps. 

#. Update the list of memcache servers in /etc/chase/proxy-server.conf for all the added proxy servers. If you run multiple memcache servers, use this pattern for the multiple IP:port listings: `10.1.2.3:11211,10.1.2.4:11211` in each proxy server's conf file.::

        [filter:cache]
        use = egg:chase#memcache
        memcache_servers = $PROXY_LOCAL_NET_IP:11211

#. Change the storage url for any users to point to the load balanced url, rather than the first proxy server you created in /etc/chase/proxy-server.conf::

        [filter:tempauth]
        use = egg:chase#tempauth
        user_system_root = testpass .admin http[s]://<LOAD_BALANCER_HOSTNAME>:<PORT>/v1/AUTH_system

#. Next, copy all the ring information to all the nodes, including your new proxy nodes, and ensure the ring info gets to all the storage nodes as well. 

#. After you sync all the nodes, make sure the admin has the keys in /etc/chase and the ownership for the ring file is correct. 

Troubleshooting Notes
---------------------
If you see problems, look in var/log/syslog (or messages on some distros). 

Also, at Rackspace we have seen hints at drive failures by looking at error messages in /var/log/kern.log. 

There are more debugging hints and tips in the :doc:`admin_guide`.

