import subprocess
import traceback
from cStringIO import StringIO

# from .
import growl

def logException(msg):
    _str = StringIO()
    traceback.print_exc(file=_str)
    _str.seek(0, 0)
    _str = _str.read()
    _growler = growl.Growler("python.app", icon="python.app")
    try:
        raise ValueError
        _growler.growl(
            "Exception message", "Exception happend: %s" % msg,
            _str, priority=2, sticky=1)
    except ValueError:
        _pop = subprocess.Popen("open -tf", shell=True, stdin=subprocess.PIPE)
        _pop.stdin.write("Error happend: %s\n%s" % (msg, _str))
        _pop.communicate()

# vim: set sts=4 sw=4 et :
