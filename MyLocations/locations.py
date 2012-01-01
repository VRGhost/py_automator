# list of locations
import os
import subprocess
import sys

class LocationObject(object):

    name = app = None


    def __init__(self, app):
        self.app = app

    ipList = ()
    def match(self):
        return any(map(lambda ip: self.app.haveIp(ip), self.ipList))

    startupApps = ()
    def doRun(self):
        if not self.startupApps:
            return
        _callables = []
        _apps = []
        for _el in self.startupApps:
            if callable(_el):
                _callables.append(_el)
            else:
                _apps.append(_el)
        [_call(self) for _call in _callables]
        self.app.startApps(_apps)

    def act(self):
        _rv = self.match()
        if _rv:
            self.doRun()
        return _rv

class ANK(LocationObject):
    name = "ANK"
    ipList = ("192.168.14.91", )

    # Obsolete

class Home_wifi(LocationObject):
    name = "Home (via wifi)"
    ipList = ("192.168.1.21", )

    startupApps = [
        lambda s: s.tryUnison()
    ]

    def tryUnison(self):
        _progPath = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "unison"))
        if _progPath not in sys.path:
            sys.path.append(_progPath)
        import doSync
        _syncer = doSync.Syncer("macbook")
        _err = _syncer.sync()
        if _err:
            self.app.forceMessage(_syncer.getPrintableLog())

class Home_ethernet(Home_wifi):
    name = "Home (via ethernet)"
    ipList = ("192.168.1.42", )

class OnTheGo(LocationObject):

    def match(self):
        return True

def getLocations():
    # Priority by order
    return (
        ANK,
        Home_ethernet,
        Home_wifi,
        OnTheGo,
    )

# vim: set sts=4 sw=4 et :
