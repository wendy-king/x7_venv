from x7x.api.connection import ApiConnection
from x7x.extras.consoles import ConsoleManager
from x7x.extras.flavors import FlavorManager
from x7x.extras.keypairs import KeypairManager
from x7x.extras.servers import ServerManager
from x7x.extras.snapshots import SnapshotManager
from x7x.extras.tenants import TenantManager
from x7x.extras.users import UserManager
from x7x.extras.usage import UsageManager
from x7x.extras.role_refs import RoleRefManager
from x7x.extras.roles import RoleManager
from x7x.extras.endpoint_templates import EndpointTemplateManager
from x7x.extras.endpoints import EndpointManager
from x7x.extras.security_groups import SecurityGroupManager
from x7x.extras.security_group_rules import SecurityGroupRuleManager
from x7x.extras.virtual_interfaces import VirtualInterfacesManager
from x7x.api.config import Config


class Extras(object):
    """
    Top-level object to access the X7 Admin API.

    Create an instance with your creds::

    >>> compute = Admin(username=USERNAME, apikey=API_KEY)

    Then call methods on its managers::

        >>> compute.servers.list()
        ...
        >>> compute.flavors.list()
        ...

    &c.
    """

    def __init__(self, **kwargs):
        self.config = self._get_config(kwargs)
        self.connection = ApiConnection(self.config)
        self.consoles = ConsoleManager(self)
        self.usage = UsageManager(self)
        self.flavors = FlavorManager(self)
        self.servers = ServerManager(self)
        self.keypairs = KeypairManager(self)
        self.snapshots = SnapshotManager(self)
        self.security_groups = SecurityGroupManager(self)
        self.security_group_rules = SecurityGroupRuleManager(self)
        self.virtual_interfaces = VirtualInterfacesManager(self)

    def authenticate(self):
        """
        Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`~x7.compute.Unauthorized` if
        the credentials are wrong.
        """
        self.connection.authenticate()

    def _get_config(self, kwargs):
        """
        Get a Config object for this API client.

        Broken out into a seperate method so that the test client can easily
        mock it up.
        """
        return Config(config_file=kwargs.pop('config_file', None),
                      env=kwargs.pop('env', None), overrides=kwargs)


class Account(object):
    """
    API to use keystone extension for tenant / user management

    Create an instance with your creds::

    >>> accounts = Account(auth_token='123', management_url='...')

    Then call methods on its managers::

        >>> accounts.tenants.list()
        ...
        >>> accounts.users.list()
        ...

    &c.
    """

    def __init__(self, **kwargs):
        self.config = self._get_config(kwargs)
        self.connection = ApiConnection(self.config)
        self.tenants = TenantManager(self)
        self.users = UserManager(self)
        self.role_refs = RoleRefManager(self)
        self.roles = RoleManager(self)
        self.endpoint_templates = EndpointTemplateManager(self)
        self.endpoints = EndpointManager(self)

    def authenticate(self):
        """
        Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`~x7.compute.Unauthorized` if
        the credentials are wrong.
        """
        self.connection.authenticate()

    def _get_config(self, kwargs):
        """
        Get a Config object for this API client.

        Broken out into a seperate method so that the test client can easily
        mock it up.
        """
        return Config(config_file=kwargs.pop('config_file', None),
                      env=kwargs.pop('env', None), overrides=kwargs)
