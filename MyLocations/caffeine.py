# from .
import appleScript

class Caffeine(object):

    def isRunning(self):
        return appleScript.isAppRunning("Caffeine")

    def isActive(self):
        if not self.isRunning():
            raise EnvironmentError("Caffeine is not running")
        return appleScript.getBoolAnswer("""
            tell application "Caffeine"
                active
            end tell
        """)

    def _setActivated(self, status):
        if not self.isRunning():
            raise EnvironmentError("Caffeine is not running")
        appleScript.execScript("""
            tell application "Caffeine"
                turn %s
            end tell
        """ % ("on" if status else "off"))

    def activate(self):
        self._setActivated(True)

    def deactivate(self):
        self._setActivated(False)

if __name__ == "__main__":
    # debug
    _caf = Caffeine()
    print _caf.isActive()

# vim: set sts=4 sw=4 et :
