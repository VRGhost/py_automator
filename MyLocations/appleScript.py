# from .
import shell

def execScript(script, wait=True):
    _commands = []
    for _line in script.splitlines():
        _line = _line.strip()
        if not _line:
            continue
        _commands.extend(("-e", _line))
    if not _commands:
        #nothing to call
        return
    _popen = shell.execute("osascript", _commands)
    if wait:
        _popen.wait()
    return _popen

def escapeString(text):
    return '"%s"' % text.replace("\\", "\\"*2).replace('"', '\\"')

# some misc handlers
def getBoolAnswer(command):
    _popen = execScript(command)
    _answer = _popen.stdout.read().strip()
    if _answer not in ("true", "false"):
        raise ValueError("Strange answer: %s (stderr=%r)" % (
            _answer, _popen.stderr.read()
        ))
    return _answer == "true"

def isAppRunning(appName):
    assert '"' not in appName
    return getBoolAnswer("""
        tell application "System Events"
            count of (every process whose name is "%s") > 0
        end tell
    """ % appName)

# vim: set sts=4 sw=4 et :
