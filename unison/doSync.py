#!/usr/bin/env python

import glob
import os
import shutil
import subprocess
import sys
import datetime

import util, executor

class Syncer(object):

    configName = _cfg = logs = args = None

    def __init__(self, configName, args):
        self.configName = configName
        self.args = args
        self._cfg = self.readConfig(configName, args)

    def readConfig(self, configName, args):
        _cfgPath = os.path.join(
            util.getEnvPath("THIS_DIR"), "cfg", configName + ".ini")
        if not os.path.exists(_cfgPath):
            raise ValueError("Config with name %s not found in %r" % (
                configName, _cfgPath))
        return util.readConfigFile(_cfgPath, args)

    def enforceProfiles(self):
        _srcDir = os.path.join(util.getEnvPath("THIS_DIR"), "profiles")
        if not os.path.isdir(_srcDir):
            raise ValueError("Directory %s does not exist.", _srcDir)
        for _file in glob.iglob(os.path.join(_srcDir, "*.prf")):
            _targ = os.path.join(
                util.getEnvPath("UNISON_DIR"), os.path.basename(_file))
            shutil.copyfile(_file, _targ)

    def constructExecutor(self, name, cfg):
        _cls = executor.guessExecutor(cfg.keys())
        return _cls(name, cfg)

    def addToLog(self, msg):
        if not self.logs:
            self.logs = []
        self.logs.append(msg)

    def normaliseExecCfg(self, config):
        _out = {}
        _cfgExtras = {}
        for (_name, _value) in config.iteritems():
            if _name.startswith("extra_setting"):
                (_name, _value) = _value.split("=", 1)
                _cfgExtras[_name.strip()] = _value.strip()
            else:
                _out[_name] = _value
        if _cfgExtras:
            _out["settings"] = _cfgExtras
        return _out

    def sync(self):
        self.enforceProfiles()
        # Run Unison
        _out = 0
        for _section in self._cfg.iterkeys():
            _usableCfg = self.normaliseExecCfg(self._cfg[_section])
            _sync = self.constructExecutor(_section, _usableCfg)
            _rv = _sync.execute()
            self.addToLog({
                "section": _section,
                "rv": _rv,
                "message": _sync.printableMessage()
            })
            _out = _out or _rv
        return _out

    def _addLineShift(self, msg, count=1):
        return "\n".join(
            ("  " * count) + _line
            for _line in msg.splitlines()
        )

    def getPrintableLog(self):
        _out = ""
        for _item in self.logs:
            _out += "\n".join((
                "==== Section %r ====" % _item["section"],
                self._addLineShift(_item["message"]),
                "  Return code: %s" % _item["rv"],
            )) + "\n"
        return _out

class SyncExecutor(object):

    def __init__(self,
        config, args, verbose, outCall):
        self._syncer = Syncer(config, args)
        self.verbose = verbose
        self.outCall = outCall

    def sync(self):
        _rv = self._syncer.sync()
        if _rv not in (0, 1) or self.verbose:
            self.sayLog(_rv)

    def sayLog(self, rc):
        if rc:
            _msg = self._syncer.getPrintableLog()
            print >>sys.stderr, _msg
        else:
            _msg = "Unison sync succeeded."
        if self.outCall:
            _exec = os.path.abspath(self.outCall)
            if not os.path.exists(_exec):
                raise RuntimeError("Path %r must exist" % _exec)
            subprocess.call([_exec, _msg])
        else:
            print _msg


def run(opts, args):
    _syncer = SyncExecutor(
        sys.argv[1],
        args,
        opts.has_key("-v"),
        opts.get("--outCall")
    )
    _syncer.sync()

if __name__ == "__main__":
    import getopt
    (_opts, _unparsed) = getopt.getopt(sys.argv[2:], ":v", [
        "outCall=", "arg=",
    ])
    assert not _unparsed
    # collect list of args
    _args = {}
    for (_name, _value) in _opts:
        if _name == "--arg":
            (_name, _value) = _value.split("=", 1)
            _args[_name] = _value
    _opts = dict(_opts)
    _lockfile = os.path.join(os.path.dirname(__file__), "sync.lock")
    if os.path.exists(_lockfile):
        print "Lock file exists, exiting without action."
	_rc = 1
    else:
        _rc = 2
        file(_lockfile, "w").write(
            "Locked at %s" % datetime.datetime.now().isoformat())
        try:
            run(_opts, _args)
            _rc = 0
        finally:
            os.unlink(_lockfile)
    exit(_rc)

# vim: set sts=4 sw=4 et :
