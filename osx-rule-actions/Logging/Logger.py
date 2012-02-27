"""Logger object: stores logs."""

from cStringIO import StringIO
import logging
import logging.handlers
import os
import sys
import traceback

import base

from . import (
    callingHandler,
    userOutput,
)

class _StreamRedirictToLog(base.Base):

    _level = None

    def __init__(self, application, level):
        super(_StreamRedirictToLog, self).__init__(application)
        self._level = level

    def write(self, msg):
        if not isinstance(msg, basestring):
            msg = repr(msg)
        self.do_log(self._level, msg.strip())


class Logger(base.Base):
    """Logger object: stores logs."""
    _rootLogger = None

    originalSysStdout = originalSysStderr = None

    def __init__(self, application):
        super(Logger, self).__init__(application)

        self._rootLogger = logging.getLogger("")
        self._rootLogger.setLevel(logging.DEBUG)
        self._installLogfile()
        self._addUserTexEditOutput()
        self._addUserGrowlOutput()

    def _installLogfile(self):
        """Add default logfile handler"""
        # Rollover is forced every 3GiB
        _logFile = logging.handlers.RotatingFileHandler(
            os.path.join(self.app.settings.log_dir, "application.log"),
            backupCount=10, maxBytes=1024**3, encoding="utf8")
        _logFile.doRollover()
        _fileFormatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        _logFile.setFormatter(_fileFormatter)
        self._rootLogger.addHandler(_logFile)

    def _addUserTexEditOutput(self):
        # add Default userspace logger
        _textFormatter = logging.Formatter("[%(asctime)s]\n%(message)s")
        _out = userOutput.TextEditOutput(self)
        _textHandler = callingHandler.CallingHandler(_out.showMsg)
        _textHandler.setFormatter(_textFormatter)
        _textHandler.setLevel(logging.CRITICAL)
        self._rootLogger.addHandler(_textHandler)

    def _addUserGrowlOutput(self):
        _out = userOutput.GrowlOutput(self)
        _handler = callingHandler.CallingHandler(_out.showMsg)
        _textFormatter = logging.Formatter(_out.getMessageFormat())
        _handler.setFormatter(_textFormatter)
        # do not set logging to DEBUG here.
        # since every time you try to growl something
        # it generates more debug log messages...
        _handler.setLevel(logging.INFO)
        self._rootLogger.addHandler(_handler)

    def install(self):
        """Install system-wide error/stream handles."""

        self.log_debug("Saving original system stdout/stderr.")
        self.originalSysStdOut = sys.stdout
        self.originalSysStdErr = sys.stderr

        self.log_debug("Replacing original system stdout/stderr.")
        sys.stdout = _StreamRedirictToLog(self.app, logging.DEBUG)
        sys.stderr = _StreamRedirictToLog(self.app, logging.ERROR)

        # if run is console, add stream loggers to original
        # app streams
        if not self.app.settings.is_daemon:
            _stdoutLogger = logging.StreamHandler(
                self.originalSysStdOut)
            _stdoutLogger.setLevel(logging.DEBUG)
            _formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
            _stdoutLogger.setFormatter(_formatter)
            self._rootLogger.addHandler(_stdoutLogger)

    # log handlers
    def debug(self, msg, args=()):
        if args:
            msg = msg % args
        self._rootLogger.debug(msg)

    def info(self, msg, args=()):
        if args:
            msg = msg % args
        self._rootLogger.info(msg)

    def error(self, msg, args=()):
        if args:
            msg = msg % args
        self._rootLogger.error(msg)

    def do_log(self, level, msg, args=()):
        if args:
            msg = msg % args
        self._rootLogger.log(level, msg)

    def exception(self, msg, args=()):
        """ Log exception amongst with error stack """
        if args:
            msg = msg % args
        _str = StringIO()
        traceback.print_exc(file=_str)
        _str.seek(0, 0)
        _str = _str.read()
        _msg = "%s\n======== Error:\n%s" % (msg, _str)
        self._rootLogger.log(logging.CRITICAL, _msg)

# vim: set sts=4 sw=4 et :
