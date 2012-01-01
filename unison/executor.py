#!/usr/bin/env python

import os
import subprocess

import util

class UnisonProcess(object):

    profile = roots = env = name = settings = None

    DEFAULT_ENV = {
        "HOME": util.getEnvPath("HOME"),
    }

    DEFAULT_SETTINGS = {
        "batch": True,
        "silent": True,
        "contactquietly": True,
    }

    PROFILE_TEMPLATE = "\n\n".join((
        "%(roots)s",
        "include %(baseProfile)s",
        "%(settings)s",
        ""
    ))

    runResult = {
        "message": "!NOT EXECUTED!",
        "rv": None,
    }

    def __init__(self, name, profile, root1, root2, settings=None, env=None):
        self.name = name
        self.profile = profile
        self.roots = map(self.normRoot, (root1, root2))

        self.env = self.DEFAULT_ENV.copy()
        if env:
            self.env.update(env)

        self.settings = self.DEFAULT_SETTINGS.copy()
        if settings:
            self.settings.update(settings)

    def normRoot(self, root):
        if root.startswith("~"):
            root = os.path.join(util.getEnvPath("HOME"), root.lstrip("~/"))
        if not os.path.isdir(root) and not root.startswith("ssh://"):
            raise ValueError("Root %s does not exist." % root)
        return root

    def toUnisonType(self, var):
        _map = {
            bool: lambda v: "true" if v else "false",
            str: lambda v: v
        }
        for (_type, _func) in _map.iteritems():
            if isinstance(var, _type):
                return _func(var)
        raise ValueError("Unknown var %r with type %r" % (
            var, var.__class__.__name__))

    def getProfileText(self):
        _roots = "\n".join(
            "root=%s" % _root
            for _root in self.roots
        )
        _settings = "\n".join(
            "%s=%s" % (_name, self.toUnisonType(_value))
            for (_name, _value) in self.settings.iteritems()
        )
        return self.PROFILE_TEMPLATE % {
            "roots": _roots,
            "baseProfile": self.profile,
            "settings": _settings,
        }

    def createTmpProfile(self):
        _name = "auto_%s.prf" % self.name
        _fileName = os.path.join(
            util.getEnvPath("UNISON_DIR"), _name)
        file(_fileName, "w").write(self.getProfileText())
        return _name

    def runUnison(self):
        _logName = "_".join(["pyUnison", self.name]) + ".log"
        _logName = os.path.join(util.getEnvPath("UNISON_DIR"), _logName)
        _logFile = file(_logName, "wb")
        _tmpProf = self.createTmpProfile()
        _args = ["unison", _tmpProf, "-ui text"]
        if "UNISONBACKUPDIR" in self.env:
            if not os.path.exists(self.env["UNISONBACKUPDIR"]):
                os.makedirs(self.env["UNISONBACKUPDIR"])
            assert os.path.isdir(self.env["UNISONBACKUPDIR"])
        _proc = subprocess.Popen(
            args=" ".join(_args),
            env=self.env,
            shell=True,
            stdout=_logFile,
            stderr=subprocess.STDOUT
        )
        _rv = _proc.wait()
        _logFile.close()
        self.runResult = {
            "rv" : _rv,
            "args": _args,
            "env": self.env,
            "log": _logName,
            "name": self.name,
        }
        return _rv

class Executor(object):
    """Base executor object."""

    _syncs = ()

    def execute(self):
        _rv = 0
        for _proc in self._syncs:
            _rv = _rv or _proc.runUnison()
        return _rv

    def allMessages(self):
        return [_proc.runResult for _proc in self._syncs]

    def printableMessage(self):
        _out = ""
        for _msg in self.allMessages():
            _out += "\n".join((
                "",
                "== %s ==" % _msg["name"],
                "  Environement: %s" % _msg["env"],
                "  Log file: %r" % _msg["log"],
                "  Args: %s" % _msg["args"],
                "  Return code: %s" % _msg["rv"],
            )) + "\n"
        return _out

class SimpleExecutor(Executor):

    def __init__(self, name, unisonArgs):
        self._syncs = [UnisonProcess(name=name, **unisonArgs)]

class MultiExecutor(Executor):

    def __init__(self, name, args):
        _rootBase = args.pop("root")
        _rootNames = [_name
            for _name in args.iterkeys()
            if _name.startswith("root")
        ]
        _rootNames.sort()
        _roots = [args.pop(_name) for _name in _rootNames]
        self._syncs = []

        _env = args.pop("env", {})
        assert "UNISONBACKUPDIR" not in _env

        for _root in _roots:
            _plainRoot = _root
            for _ch in (os.sep, " ", "~"):
                _plainRoot = _plainRoot.replace(_ch, "_")

            _thisEnv = _env.copy()
            if util.envIsSet("UNISON_BACKUP_ROOT"):
                _thisEnv["UNISONBACKUPDIR"] = os.path.join(
                    util.getEnvPath("UNISON_BACKUP_ROOT"),
                    name,
                    _plainRoot
                )
            args["env"] = _thisEnv

            _proc = UnisonProcess(
                name="".join((name, _plainRoot)),
                root1=_rootBase,
                root2=_root,
                **args
            )
            self._syncs.append(_proc)

def guessExecutor(cfgKeys):
    _keys = frozenset(cfgKeys)
    if _keys == frozenset(["profile", "root1", "root2"]):
        _rv = SimpleExecutor
    elif _keys.issuperset(["profile", "root", "root1"]):
        _rv = MultiExecutor
    else:
        raise ValueError("Failed to guess for %s" % cfgKeys)
    return _rv

# vim: set sts=4 sw=4 et :
