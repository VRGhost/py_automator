from subprocess import Popen, PIPE
import re
import sys

# from .
import growl
import caffeine
import appleScript
import exceptionHandler
import locations

class Guesser(object):

    growler = caffeine = location = None
    powerProfiles = activePowerProfile = None
    ifconfigText = ""
    onBatt = False
    _forcedMessages = None

    def __init__(self, isDaemon):
        self.growler = growl.Growler(
            "Setting guesser", "System Preferences.app")
        self.isDaemon = isDaemon
        self._forcedMessages = []
        self.caffeine = caffeine.Caffeine()
        self._getIfconfig()
        self._getBatteryState()
        _fullFun = lambda: (self.coffeeIfDocked(), self.canHaveFun())

    def isDaemonic(self):
        return self.isDaemon

    def startApps(self, apps):
        for _name in apps:
            if '"' in _name:
                raise Excetion("Strange app name %s" % _name)
        _cmd = "\n".join(map(
            lambda app: 'tell application "%s" to launch' % app, apps))
        appleScript.execScript(_cmd)

    def _getStdout(self, cmd):
        _pop = Popen(cmd, shell=True, stdout=PIPE)
        _pop.wait()
        return _pop.stdout.read().strip()

    def _getIfconfig(self):
        self.ifconfigText = self._getStdout("ifconfig")

    def _getBatteryState(self):
        _text = self._getStdout("pmset -g")
        _match= re.search(r"Active Profiles:\n(([\s\w]+-?\d+\*?\n)+)",
            _text, re.M)
        if not _match:
            return
        _profiles = _match.group(1)
        if not _profiles:
            return
        _gotProfiles = {}
        _activeProfile = None
        for _profile in _profiles.splitlines():
            _profile = _profile.strip()
            _match = re.match(r"(\w+(?:\s+\w+)*)\s+(-?\d+)(\*?)", _profile)
            if not _match:
                continue
            (_name, _type, _active) = _match.groups()
            _gotProfiles[_name] = {"type": _type, "active": _active}
            if _active:
                _activeProfile = _name
        self.powerProfiles = _gotProfiles
        self.activePowerProfile = _activeProfile
        self.onBatt = "battery" in _activeProfile.lower()

    def growlLocationGuessed(self, title, text, sticky=False):
        self.growler.growl("Location guessed", title, text, sticky=sticky)

    def haveIp(self, addr):
        # Return `True` if given address is issued to this box
        _substr = "inet %s" % addr
        return _substr in self.ifconfigText

    def guess(self):
        for _cls in locations.getLocations():
            _obj = _cls(self)
            if _obj.act():
                self.location = _obj.name
                break
        else:
            raise Exception("Unknwon location")
        if not self.isDaemonic() or self._forcedMessages:
            self.growlStatus()

    def growlStatus(self):
        if self.location:
            _title = "Seems to be %s" % self.location
        else:
            _title = "Unknown location"
        _state = ["Running on %s power" % ("battery" if self.onBatt else "AC")]

        if self.caffeine.isRunning():
            _state.append("Caffeine is %s " %
                ("active" if self.caffeine.isActive() else "not active"))

        if self._forcedMessages:
            _state.extend([
                "*** FORCED MESSAGES ***",
                "\n------\n".join(self._forcedMessages),
            ])
        self.growlLocationGuessed(
            _title, "\n".join(_state), sticky=self._forcedMessages)

    def coffeeIfDocked(self):
        self.caffeine.setActivated(not self.onBatt)

    def forceMessage(self, msg):
        self._forcedMessages.append(msg)

if __name__ == "__main__":
    try:
        _guesser = Guesser("--daemonic" in sys.argv)
        _guesser.guess()
    except:
        exceptionHandler.logException("Unhandled exception")

# vim: set sts=4 sw=4 et :
