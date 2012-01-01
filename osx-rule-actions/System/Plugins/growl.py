"""Growl plugin."""


from . import PluginApp

class GrowlConfiguredIncompitelyError(ValueError):
    """Its in the name."""

class Growl(PluginApp):
    """Growl plugin."""

    controlledAppName = "Growl"

    appName = icon = None
    notificationTypes = ()

    def setGlobalGrowlingApplicationOptions(self, appName, icon=None):
        self.appName = appName
        self.setIcon(icon)

    def setIcon(self, icon):
        self.icon = icon
        try:
            self.register()
        except GrowlConfiguredIncompitelyError:
            pass

    def register(self):
        if not self.notificationTypes:
            raise GrowlConfiguredIncompitelyError("No notification types defined!")
        if not self.isRunning():
            raise EnvironmentError("Growl is not running")
        _wrap = self.appleScript.escapeString
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
            'tell application "%s"' % self.controlledAppName,
            _tellCmd % _substArgs,
            'end tell',
        ))
        self.appleScript.execScript(_appleScript)

    def growl(self, type, title, text, priority=0, sticky=False):
        if type not in self.notificationTypes:
            self.notificationTypes += (type, )
            self.register()
        _wrap = self.appleScript.escapeString
        _priority = min(max(priority, -2), 2)
        _appleScript = """
            tell application "%(targetApp)s"
                notify \
                    with name %(type)s \
                    title %(title)s \
                    description %(body)s \
                    application name %(appName)s \
                    sticky %(sticky)s \
                    priority %(priority)i 
            end tell
            """ % {
                "targetApp": self.controlledAppName,
                "appName": _wrap(self.appName),
                "type": _wrap(type),
                "title": _wrap(title),
                "body": _wrap(text),
                "sticky": "true" if sticky else "false",
                "priority": _priority,
            }
        self.appleScript.execScript(_appleScript)

# vim: set sts=4 sw=4 et :
