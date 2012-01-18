Python bindings to the Rackspace Cloud Servers API
==================================================

This is a client for the X7 Compute API used by Rackspace Cloud and
others. There's a Python API (the ```x7.compute`` module), and a
command-line program (installed as ``x7-compute``). Each implements the
entire X7 Compute API (as well as a few Rackspace-only addons).

`Full documentation is available`__.

__ http://x7compute.rtfd.org/

You'll also probably want to read `Rackspace's API guide`__ (PDF) -- the first
bit, at least -- to get an idea of the concepts. Rackspace is doing the cloud
hosting thing a bit differently from Amazon, and if you get the concepts this
library should make more sense.

__ http://docs.rackspacecloud.com/servers/api/cs-devguide-latest.pdf

Development takes place on GitHub__. Bug reports and patches may be filed there.

__ http://github.com/jacobian/x7.compute

.. contents:: Contents:
   :local:

Command-line API
----------------

Installing this package gets you a shell command, ``x7-compute``, that
you can use to interact with Rackspace.

You'll need to provide your Rackspace username and API key. You can do this
with the ``--username`` and ``--apikey`` params, but it's easier to just set
them as environment variables::

    export X7_COMPUTE_USERNAME=jacobian
    export X7_COMPUTE_API_KEY=yadayada

You'll find complete documentation on the shell by running
``cloudservers help``::

    usage: x7-compute [--username USERNAME] [--apikey APIKEY] <subcommand> ...

    Command-line interface to the X7 Compute API.

    Positional arguments:
      <subcommand>
        backup-schedule     Show or edit the backup schedule for a server.
        backup-schedule-delete
                            Delete the backup schedule for a server.
        boot                Boot a new server.
        delete              Immediately shut down and delete a server.
        flavor-list         Print a list of available 'flavors' (sizes of
                            servers).
        help                Display help about this program or one of its
                            subcommands.
        image-create        Create a new image by taking a snapshot of a running
                            server.
        image-delete        Delete an image.
        image-list          Print a list of available images to boot from.
        ip-share            Share an IP address from the given IP group onto a
                            server.
        ip-unshare          Stop sharing an given address with a server.
        ipgroup-create      Create a new IP group.
        ipgroup-delete      Delete an IP group.
        ipgroup-list        Show IP groups.
        ipgroup-show        Show details about a particular IP group.
        list                List active servers.
        reboot              Reboot a server.
        rebuild             Shutdown, re-image, and re-boot a server.
        rename              Rename a server.
        resize              Resize a server.
        resize-confirm      Confirm a previous resize.
        resize-revert       Revert a previous resize (and return to the previous
                            VM).
        root-password       Change the root password for a server.
        show                Show details about the given server.

    Optional arguments:
      --username USERNAME   Defaults to env[X7_COMPUTE_USERNAME].
      --apikey APIKEY       Defaults to env[X7_COMPUTE_API_KEY].

    See "x7-compute help COMMAND" for help on a specific command.

Python API
----------

There's also a `complete Python API`__.

__ http://x7compute.rtfd.org/

By way of a quick-start::

    >>> import x7.compute
    >>> compute = x7.compute.Compute(USERNAME, API_KEY)
    >>> compute.flavors.list()
    [...]
    >>> compute.servers.list()
    [...]
    >>> s = compute.servers.create(image=2, flavor=1, name='myserver')

    ... time passes ...

    >>> s.reboot()

    ... time passes ...

    >>> s.delete()

FAQ
---

What's wrong with libcloud?

    Nothing! However, as a cross-service binding it's by definition lowest
    common denominator; I needed access to the X7-specific APIs (shared
    IP groups, image snapshots, resizing, etc.). I also wanted a command-line
    utility.

What's new?
-----------

See `the release notes <http://x7compute.readthedocs.org/en/latest/releases.html>`_.
