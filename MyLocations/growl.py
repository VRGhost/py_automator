#         The basics for the Growl Applescript came from the Growl
#         documentation at:
#             <http://growl.info/documentation/applescript-support.php>
#-----------------------------------------------------------------------------

import subprocess

# from .
import appleScript

class Growler(object):

    appName = icon = None
    notificationTypes = ()

    def __init__(self, appName, icon=None):
        self.appName = appName
        self.setIcon(icon)

    def setIcon(self, icon):
        self.icon = icon
        try:
            self.register()
        except ValueError:
            pass

    def isGrowlRunning(self):
        return appleScript.isAppRunning("GrowlHelperApp")

    def register(self):
        if not self.notificationTypes:
            raise ValueError("No notification types defined!")
        if not self.isGrowlRunning():
            raise EnvironmentError("Growl is not running")
        _wrap = appleScript.escapeString
        _substArgs = {
            "progName": _wrap(self.appName),
            "noteList": ", ".join(map(_wrap, self.notificationTypes)),
        }
        _tellCmd = \
            "register as application %(progName)s \
                all notifications {%(noteList)s} \
                default notifications {%(noteList)s}"
        if self.icon:
            _tellCmd += " icon of application %(icon)s"
            _substArgs["icon"] = _wrap(self.icon)
        _appleScript = "\n".join((
            'tell application "GrowlHelperApp"',
            _tellCmd % _substArgs,
            'end tell',
        ))
        appleScript.execScript(_appleScript)

    def growl(self, type, title, text, priority=0, sticky=False):
        if type not in self.notificationTypes:
            self.notificationTypes += (type, )
            self.register()
        _wrap = appleScript.escapeString
        _priority = min(max(priority, -2), 2)
        _appleScript = """
            tell application "GrowlHelperApp"
                notify \
                    with name %(type)s \
                    title %(title)s \
                    description %(body)s \
                    application name %(appName)s \
                    sticky %(sticky)s \
                    priority %(priority)i
            end tell
            """ % {
                "appName": _wrap(self.appName),
                "type": _wrap(type),
                "title": _wrap(title),
                "body": _wrap(text),
                "sticky": "yes" if sticky else "no",
                "priority": _priority,
            }
        appleScript.execScript(_appleScript)


if __name__ == "__main__":
    # debug
    _growler = Growler("Growler test")
    _growler.growl("Type1", "Test", "Hello world")
    _growler.growl("Type2", "Test", "Hello world")

# vim: set sts=4 sw=4 et :
