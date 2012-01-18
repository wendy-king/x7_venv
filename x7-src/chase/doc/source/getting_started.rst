===============
Getting Started
===============

-------------------
System Requirements
-------------------

Chase development currently targets Ubuntu Server 10.04, but should work on 
most Linux platforms with the following software:

* Python 2.6
* rsync 3.0

And the following python libraries:

* Eventlet 0.9.8
* WebOb 0.9.8
* Setuptools
* Simplejson
* Xattr
* Nose
* Sphinx
* netifaces

-------------
Getting Chase
-------------

Chase's source code is hosted on github and managed with git.  The current trunk can be checked out like this:

    ``git clone https://github.com/x7/chase.git``

A source tarball for the latest release of Chase is available on the `launchpad project page <https://launchpad.net/chase>`_.

Prebuilt packages for Ubuntu are available starting with Natty, or from PPAs for earlier releases.

* `Chase Latest Release PPA <https://launchpad.net/~chase-core/+archive/release>`_
* `Chase Current Trunk PPA <https://launchpad.net/~chase-core/+archive/trunk>`_

-----------
Development
-----------

To get started with development with Chase, or to just play around, the
following docs will be useful:

* :doc:`Chase All in One <development_saio>` - Set up a VM with Chase installed
* :doc:`Development Guidelines <development_guidelines>`

----------
Production
----------

If you want to set up and configure Chase for a production cluster, the following doc should be useful:

* :doc:`Multiple Server Chase Installation <howto_installmultinode>`
