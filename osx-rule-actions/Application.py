"""Main application object."""

from cStringIO import StringIO
import os
import subprocess
import traceback

# Project imports
from Logging import Logger
from System import System

class _AppConfig(object):
    """Read-only application config.

    Implements both dictionary and object accessors.
    """

    def __init__(self, data):
        self.__data = data

    __repr__ = lambda self: "<%s:%s>" % (self.__class__.__name__, repr(self.__data))

    def __getitem__(self, name):
        return self.__data[name]

    def __getattr__(self, name):
        return self.__data[name]


class Application(object):

    settings = None
    log = system = None # Placeholders to be filled later.
    growl = None # Can be 'None' if no Growl found.

    def __init__(self, is_daemon=True):
        self.settings = self._assembleSettings(is_daemon=is_daemon)
        self.log = Logger(self)
        self.log.install()
        self.log.debug("Logging installed.")
        self.system = System(self)
        self.log.debug("Application initialisation finished.")

    def _assembleSettings(self, is_daemon):
        """Assemple application settings (such as log dir, etc)."""
        return _AppConfig({
            "is_daemon": is_daemon,
            "log_dir": os.path.join(os.path.dirname(__file__), "logs"),
        })

    def doWork(self):
        """Called when caller wants for application to perform its actual functionality."""
        self.system.loadPlugins()
        self.log.debug("System plugins loaded.")
        # Growl app is so specific and widespread that it makes sense to
        # care about it even on the top application level.
        if self.system.plugins.growl.isRunning():
            self.growl = self.system.plugins.growl
            self.growl.setGlobalGrowlingApplicationOptions("OsXRuleActions")
        # Now to call call user configuration.
        from config import main as mainConfig
        try:
            mainConfig.execute(self.system)
        except:
            self.log.exception("Error happened during config run.")

    @classmethod
    def consoleRun(cls, options):
        """Called when application is initialized from console."""
        _app = cls(is_daemon=options.is_daemon)
        try:
            _app.doWork()
        except:
            _app.showBadException("Error in main application loop.")

    def showBadException(self, msg):
        """Show top-level exception. Called only when everything else fails."""
        _str = StringIO()
        traceback.print_exc(file=_str)
        _str.seek(0, 0)
        _str = _str.read()
        _pop = subprocess.Popen("open -tf", shell=True, stdin=subprocess.PIPE)
        _pop.stdin.write("Error happend: %s\n%s" % (msg, _str))
        _pop.communicate()

# vim: set sts=4 sw=4 et :
