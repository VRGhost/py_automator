"""Airport plugin."""

from collections import defaultdict

from . import Plugin

class AirPort(Plugin):
    """AirPort info plugin."""

    airportBinary = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/airport"
    _data = None

    @property
    def data(self):
        """Auto-caching virtual property"""
        if not self._data:
            self._data = self._getData()
        return self._data

    def _getData(self):
        _rv = {}
        _out = self.sys.shell.execute(self.airportBinary, ["-I"])
        _out.wait()
        _stats = _out.stdout.read()
        for _line in _stats.splitlines():
            _line = _line.strip()
            if not _line:
                continue
            (_name, _val) = _line.split(":", 1)
            _rv[_name.strip()] = _val.strip()
        return defaultdict(lambda: None, _rv)

    def __getattr__(self, name):
        return self.data[name]

# vim: set sts=4 sw=4 et :
