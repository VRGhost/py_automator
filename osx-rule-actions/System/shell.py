"""Shell wrapper."""

import subprocess

from . import element

class ShellWrapper(element.Element):

    _execCache = {}

    _standardRunArgs = {
        # if this buffer size is not enough and subprocess freezes,
        # than you're doing something wrong.
        "bufsize": 2**10,
        "stdout": subprocess.PIPE,
        "stdin": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }

    def _escapeShellArg(self, string):
        # priority by sequence!
        _escSymb = "\\"
        _chars = (_escSymb, "$", "`", '"')
        for _el in _chars:
            string = string.replace(_el, _escSymb + _el)
        return '"%s"' % string

    def _getExecutable(self, cmd):
        if cmd not in self._execCache:
            _proc = self.execute("which", (cmd, ), forbidLookup=True)
            _proc.wait()
            _path = _proc.stdout.read().strip()
            self._execCache[cmd] = _path
        return self._execCache[cmd]

    def execute(self, cmd, args=(), forbidLookup=False):
        assert cmd
        if forbidLookup:
            _cmd = cmd
        else:
            _cmd = self._getExecutable(cmd)
        _parts = (_cmd, ) + tuple(args)
        _commandline = " ".join(map(self._escapeShellArg, _parts))
        self.log_debug("Executing command %r.", _commandline)
        _popen = subprocess.Popen(
            args=_commandline,
            shell=True, **self._standardRunArgs
        )
        return _popen


# vim: set sts=4 sw=4 et :
