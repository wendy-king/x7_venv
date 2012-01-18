The :program:`x7-compute` shell utility
==============================================

.. program:: x7-compute
.. highlight:: bash

The :program:`x7-compute` shell utility interacts with X7
Compute servers from the command line. It supports the entirety of the
X7 Compute API (plus a few Rackspace-specific additions), including
some commands not available from the Rackspace web console.

To try this out, you'll need a `Rackspace Cloud`__ account — or your own
install of X7 Compute (also known as Engine). If you're using Rackspace
you'll need to make sure to sign up for both Cloud Servers *and* Cloud Files
-- Rackspace won't let you get an API key unless you've got a Cloud Files
account, too. Once you've got an account, you'll find your API key in the
management console under "Your Account".

__ http://rackspacecloud.com/

You'll need to provide :program:`x7-compute` with your Rackspace
username and API key. You can do this with the :option:`--username` and
:option:`--apikey` options, but it's easier to just set them as environment
variables by setting two environment variables:

.. envvar:: X7_COMPUTE_USERNAME

    Your Rackspace Cloud username.

.. envvar:: X7_COMPUTE_API_KEY

    Your API key.

For example, in Bash you'd use::

    export CX7_COMPUTE_USERNAME=yourname
    export CX7_COMPUTE_API_KEY=yadayadayada
    
From there, all shell commands take the form::
    
    x7-compute <command> [arguments...]

Run :program:`x7-compute help` to get a full list of all possible
commands, and run :program:`x7-compute help <command>` to get detailed
help for that command.
