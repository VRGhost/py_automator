"""Base class for all non-Application objects in application."""

import Application

class Base(object):

    app = None

    def __init__(self, parent):
        if isinstance(parent, Application.Application):
            # Yep, that's application
            _app = parent
        else:
            _app = parent.app
        self.app = _app

    def log_debug(self, msg, *args):
        """Log DEBUG message."""
        self.app.log.debug(msg, args)

    def log_info(self, msg, *args):
        """Log INFO message."""
        self.app.log.info(msg, args)

    def log_error(self, msg, *args):
        """Log ERROR message."""
        self.app.log.error(msg, args)

    def do_log(self, level, msg, *args):
        """Log ERROR message."""
        self.app.log.do_log(level, msg, args)

# vim: set sts=4 sw=4 et :
