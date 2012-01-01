"""Airport plugin."""

from collections import defaultdict
import re

from . import Plugin

class Samba(Plugin):
    """Samba plugin."""

    def __init__(self, *args, **kwargs):
        super(Samba, self).__init__(*args, **kwargs)
        self._hosts = {}

    def getIpFor(self, smbName):
        """Return IP addres of machine with given samba name."""
        if smbName not in self._hosts:
            self._hosts[smbName] = self._getIpFor(smbName)
        return self._hosts[smbName]

    def _getIpFor(self, name):
        _out = self.sys.shell.execute("smbutil", ["lookup", name])
        _out.wait()
        if _out.returncode != 0:
            raise Exception("smbutil return code %r" % _out.returncode)
        _output = _out.stdout.read()
        _match = re.search("IP address of %s: ([0-9.]+)\n" % name, _output)
        if _match:
            return _match.group(1)
        else:
            raise Exception(
                "Failed to find IP addres for %r, " \
                "smbutil message: %r" % (
                    name, _output
            ))


# vim: set sts=4 sw=4 et :
