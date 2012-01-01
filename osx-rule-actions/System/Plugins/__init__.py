"""Plugin module contains plugins for this program to be able to use
different system functions and to obtain different system state parameters.
"""

import glob
import os

from .. import element

class Plugin(element.Element):
    """Base class for plugin."""

class PluginApp(Plugin):
    """Plugin regarding single OS X user application."""

    controlledAppName = None
    # Main means of communication with user programs is usually
    # applescript.
    appleScript = property(lambda s: s.sys.appleScript)


    _appRunStatus = None
    def isRunning(self):
        """Return if given application is running."""
        # the result is cached - it is assumed that status of application
        # is not changed during program run.
        if self._appRunStatus is None:
            self._appRunStatus = self.sys.appleScript.isAppRunning(self.controlledAppName)
        return  self._appRunStatus

def get_plugins():
    """Return dictionary for all found plugins."""
    _rv = {}
    # get list of files in this 'Plugins' directory
    _pluginDir = os.path.dirname(__file__)
    _fnames = set()
    for _ext in (".py", ".pyc"):
        _files = glob.glob(os.path.join(_pluginDir, "*" + _ext))
        _names = map(lambda el: os.path.splitext(os.path.os.path.basename(el))[0], _files)
        _fnames.update(_names)
    # Import all non-magic files and get plugin class from it.
    _modulePath = ("System", "Plugins")
    for _name in _fnames:
        if _name.startswith("__"):
            continue
        _path = _modulePath + (_name, )
        _module = __import__(".".join(_path))
        for _el in _path[1:]:
            _module = getattr(_module, _el)
        for _objName in dir(_module):
            if _objName.lower() == _name.lower():
                # Found needed plugin object.
                _rv[_objName] = getattr(_module, _objName)
                break
        else:
            raise ValueError("%r object not found in %r module" % (_path, _name))
    return _rv

# vim: set sts=4 sw=4 et :
