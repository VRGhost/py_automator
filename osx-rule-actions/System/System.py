"""[Operating] System state determining object."""

from base import Base

from . import (
    appleScript,
    shell,
    Plugins,
)

class _AttrDict(dict):

    def __getattr__(self, name):
        return self[name]

class System(Base):
    """Operating system-representing entity."""

    shell = appleScript = None

    plugins = None

    def __init__(self, app):
        super(System, self).__init__(app)
        self.plugins = _AttrDict()
        # Init standard bindngs.
        self.shell = shell.ShellWrapper(self)
        self.appleScript = appleScript.ApplescriptRunner(self)
        self.log_debug("Base system handlers initialised.")

    def loadPlugins(self):
        _plugins = Plugins.get_plugins()
        _names = sorted(_plugins.keys())
        for _name in _names:
            self.log_debug("Loading system plugin %r.", _name)
            self.plugins[_name.lower()] = _plugins[_name](self)
        self.log_debug("%i plugins loaded in total: %s", len(_plugins), _plugins.keys())


# vim: set sts=4 sw=4 et :
