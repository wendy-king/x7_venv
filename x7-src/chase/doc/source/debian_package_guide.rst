=======================================================
Building and Deploying Custom Debian packages for Chase
=======================================================

This documents setting up the prerequisites, downloading the code and building
Debian packages necessary to deploy the various components of the chase 
project code.  These steps were done on a server running 
*Ubuntu 10.04 LTS (Lucid Lynx)*, but should give a good idea what to do on 
other distros.

------------------------------------------
Instructions for Deploying Chase-Core PPAs
------------------------------------------

These packages are built from the current development branch "trunk" 

* Add chase-core/ppa repository. As root:::

       apt-get install python-software-properties
       add-apt-repository ppa:chase-core/trunk
       apt-get update

* Install the chase base packages::

       apt-get install python-chase
       apt-get install chase

* Install the chase packages depending on your implementations::

       apt-get install chase-auth
       apt-get install chase-proxy
       apt-get install chase-account
       apt-get install chase-container
       apt-get install chase-object

* Copy sample configuration files to `/etc/chase` directory 
  and rename them to `*.conf files`::
     
       cp -a /usr/share/doc/chase/*.conf-sample /etc/chase/ 
       cd /etc/chase ; rename 's/\-sample$//' *.conf-sample

* For servers running the chase-account, chase-container or 
  chase-object the rsync.conf file should be moved to 
  the `/etc` directory::

       cd /etc/chase
       mv rsyncd.conf /etc

* Modify configuration files to meet your implementation requirements
  the defaults have been not been geared to a multi-server implementation.

---------------------------------------------------
Instructions for Building Debian Packages for Chase
---------------------------------------------------

* Add chase-core/ppa repository and install prerequisites. As root::

       apt-get install python-software-properties
       add-apt-repository ppa:chase-core/release
       apt-get update
       apt-get install curl gcc bzr python-configobj python-coverage python-dev python-nose python-setuptools python-simplejson python-xattr python-webob python-eventlet python-greenlet debhelper python-sphinx python-all python-openssl python-pastedeploy python-netifaces bzr-builddeb

* As you

  #. Tell bzr who you are::

       bzr whoami '<Your Name> <youremail@.example.com>'
       bzr lp-login <your launchpad id>

  #. Create a local bazaar repository for dev/testing:: 

       bzr init-repo chase

  #. Pull down the chase/debian files::

       cd chase 
       bzr branch lp:~chase-core/chase/debian

  #. If you want to merge in a branch::
     
       cd debian
       bzr merge lp:<path-to-branch>
  
  #. Create the debian packages:: 
  
       cd debian 
       bzr bd --builder='debuild -uc -us'
 
  #. Upload packages to your target servers::
 
       cd .. 
       scp *.deb root@<chase-target-server>:~/.


----------------------------------------------------
Instructions for Deploying Debian Packages for Chase
----------------------------------------------------

* On a Target Server, As root:

  #. Setup the chase ppa::
 
       add-apt-repository ppa:chase-core/release
       apt-get update

  #. Install dependencies::
 
       apt-get install rsync python-openssl python-setuptools python-webob
       python-simplejson python-xattr python-greenlet python-eventlet
       python-netifaces

  #. Install base packages::

       dpkg -i python-chase_<version>_all.deb 
       dpkg -i chase_<version>_all.deb

  #. Install packages depending on your implementation::

       dpkg -i chase-auth_<version>_all.deb    
       dpkg -i chase-proxy_<version>_all.deb
       dpkg -i chase-account_<version>_all.deb  
       dpkg -i chase-container_<version>_all.deb  
       dpkg -i chase-object_<version>_all.deb  
       dpkg -i chase-doc_<version>_all.deb

  #. Copy sample configuration files to `/etc/chase` directory 
     and rename them to `*.conf files`::

       cp -a /usr/share/doc/chase/*.conf-sample /etc/chase/ 
       cd /etc/chase 
       rename 's/\-sample$//' *.conf-sample

  #. For servers running the chase-account, chase-container or 
     chase-object the rsync.conf file should be moved to 
     the `/etc` directory::

       cd /etc/chase/ 
       mv rsyncd.conf /etc

  #. Modify configuration files to meet your implementation requirements
     the defaults have been not been geared to a multi-server implementation.
