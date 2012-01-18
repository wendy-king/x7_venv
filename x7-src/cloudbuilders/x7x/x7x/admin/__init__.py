from x7x.api.connection import ApiConnection
from x7x.admin.networks import NetworkManager
from x7x.admin.projects import ProjectManager
from x7x.admin.services import ServiceManager
from x7x.admin.servers import ServerManager
from x7x.admin.flavors import FlavorManager
from x7x.admin.quotas import QuotaSetManager
from x7x.api.config import Config


class Admin(object):
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
        self.projects = ProjectManager(self)
        self.services = ServiceManager(self)
        self.flavors = FlavorManager(self)
        self.quota_sets = QuotaSetManager(self)
        self.servers = ServerManager(self)
        self.networks = NetworkManager(self)

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
