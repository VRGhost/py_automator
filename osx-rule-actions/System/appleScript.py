from . import element

class ApplescriptRunner(element.Element):

    def escapeString(self, text):
        """Escape string constant for applescript."""
        return '"%s"' % text.replace("\\", "\\"*2).replace('"', '\\"')

    def execScript(self, script, wait=True):
        _commands = []
        for _line in script.splitlines():
            _line = _line.strip()
            if not _line:
                continue
            _commands.extend(("-e", _line))
        if not _commands:
            #nothing to call
            return
        self.log_debug("Executing applescript:\n----\n%s\n----", script)
        _popen = self.sys.shell.execute("osascript", _commands)
        if wait:
            _popen.wait()
        return _popen


    ##### Some general handlers (only widely usable ones). ######

    def getBoolAnswer(self, command):
        """If applescript returns only bool answer, convert it into
        Python boolean."""
        _popen = self.execScript(command)
        _answer = _popen.stdout.read().strip()
        if _answer not in ("true", "false"):
            raise ValueError("Strange answer: %s (stderr=%r)" % (
                _answer, _popen.stderr.read()
            ))
        return _answer == "true"

    def isAppRunning(self, appName):
        """Return if given application is running."""
        self.log_debug("Checking if app %r is running", appName)
        assert '"' not in appName
        return self.getBoolAnswer("""
            tell application "System Events"
                count of (every process whose name is "%s") > 0
            end tell
        """ % appName)

# vim: set sts=4 sw=4 et :
