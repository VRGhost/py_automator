"""Network info plugin."""

import re

from . import Plugin

class Network(Plugin):
    """Network info plugin."""

    _data = None

    @property
    def data(self):
        """Auto-caching virtual property"""
        if not self._data:
            self._data = self._getData()
        return self._data

    def _getData(self):
        _rv = {}
        _out = self.sys.shell.execute("ifconfig")
        _stats = _out.stdout.read()

        _config = None
        for _line in _stats.splitlines():
            _line = _line.strip()
            if not _line:
                continue
            _match = re.match("^(\w+):\s+flags=(\d+)<(.*?)>\s+mtu\s+(\d+)$", _line)
            if _match:
                (_name, _flag1, _flags2, _mtu) = _match.groups()
                _rv[_name] = _config = {
                    "flags": [int(_flag1)] + map(lambda el: el.strip(), _flags2.split(",")),
                    "mtu": int(_mtu),
                    "inet": [],
                }
            elif _line.startswith("inet"):
                (_inet, _addr, _parts) = _line.split(" ", 2)
                assert _inet.startswith("inet"), _inet
                _parts = _parts.split()
                _opts = dict(zip(_parts[::2], _parts[1::2]))
                _config["inet"].append({
                    "addr": _addr,
                    "config": _opts,
                })
            elif _line.startswith("ether"):
                (_ether, _addr) = _line.split()
                assert _ether == "ether", _ether
                _config["ether"] = _addr.strip()
            else:
                while _line:
                    _match = re.match("^(.*?):(.*?)(\s+(.*?:.*))?$", _line)
                    (_name, _value) = _match.groups()[:2]
                    _line = (_match.groups() + ("", ))[2]
        return _rv

    def __getattr__(self, name):
        return self.data[name]

    def haveIp(self, ip):
        for _val in self.data.iteritems():
            for _inet in _val["inet"]:
                if _inet["addr"] == ip:
                    return True
        return False

# vim: set sts=4 sw=4 et :
