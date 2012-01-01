"""Calling handler for log output via call of provided function."""

from cStringIO import StringIO
import logging.handlers

class CallingHandler(logging.StreamHandler):

    _func = _stream = None

    def __init__(self, function):
        self._func = function
        self._stream = StringIO()
        logging.StreamHandler.__init__(self, self._stream)

    def flush(self):
        self._stream.seek(0, 0)
        _msg = self._stream.read().strip()
        if _msg:
            self._func(_msg)
        # force overwrite of successive data
        self._stream.truncate(0)

# vim: set sts=4 sw=4 et :
