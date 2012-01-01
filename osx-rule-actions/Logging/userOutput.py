"""Logger object: stores logs."""

import subprocess


import base

class UserspaceOutput(base.Base):
    """Base output handler for showing logs to user"""

    def showMsg(self, msg):
        raise NotImplementedError


class TextEditOutput(UserspaceOutput):

    def showMsg(self, msg):
        _pop = subprocess.Popen("open -tf", shell=True, stdin=subprocess.PIPE)
        _pop.stdin.write("=== Please send this to osx-rule-actions developers ===\n\n\n%s" % msg)
        _pop.communicate()

class GrowlOutput(UserspaceOutput):


    def getMessageFormat(self):
        """Return format for formatter that will format messages to this output."""
        return "%(levelname)s|||%(message)s"

    def showMsg(self, msg):
        _growl = self.app.growl
        if _growl and _growl.isRunning():
            (_level, _msg) = msg.split("|||", 1)
            _header = _msg.splitlines()[0].strip()
            _growl.growl(_level.title(), _header, _msg)

# vim: set sts=4 sw=4 et :
