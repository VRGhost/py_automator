import subprocess


class ShellWrapper(object):

    _execCache = {}
    exportedHandlers = (
        "execute",
    )

    def escapeShellArg(self, string):
        # priority by sequence!
        _escSymb = "\\"
        _chars = (_escSymb, "$", "`", '"')
        for _el in _chars:
            string = string.replace(_el, _escSymb + _el)
        return '"%s"' % string

    def getExecutable(self, cmd):
        if cmd not in self._execCache:
            _proc = self.execute("which", (cmd, ), forbidLookup=True)
            _proc.wait()
            _path = _proc.stdout.read().strip()
            self._execCache[cmd] = _path
        return self._execCache[cmd]

    def execute(self, cmd, args=(), forbidLookup=False):
        assert cmd
        _standardArgs = {
            "bufsize": 2**10,
            "stdout": subprocess.PIPE,
            "stdin": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }
        if forbidLookup:
            _cmd = cmd
        else:
            _cmd = self.getExecutable(cmd)
        _parts = (cmd, ) + tuple(args)
        _popen = subprocess.Popen(
            args=" ".join(map(self.escapeShellArg, _parts)),
            shell=True, **_standardArgs
        )
        return _popen










##################
##################
# init global object

_wrapper = ShellWrapper()
for _name in _wrapper.exportedHandlers:
    globals()[_name] = getattr(_wrapper, _name)

# vim: set sts=4 sw=4 et :
