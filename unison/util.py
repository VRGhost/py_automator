from ConfigParser import ConfigParser, RawConfigParser
import os
import sys

_ENV = {
    "HOME": os.path.expanduser("~"),
    "THIS_DIR": os.path.abspath(os.path.dirname(__file__)),
}

# Guess UNISON_DIR
if sys.platform == "darwin":
    _unisonDir = os.path.join(_ENV["HOME"],
        "Library", "Application Support", "Unison")
elif sys.platform.startswith("linux"):
    _unisonDir = os.path.join(_ENV["HOME"], ".unison")
else:
    raise OSError("Can't guess UNISON_DIR for %r" % sys.platform)

_ENV["UNISON_DIR"] = _unisonDir

def normPath(root):
    if root.startswith("~"):
        root = os.path.join(envvars.HOME, root.lstrip("~/"))
    else:
        root = os.path.abspath(root)
    return root

def getEnvPath(name):
    return normPath(_ENV[name])

def setEnv(name, value):
    global _ENV
    _ENV[name] = value

def envIsSet(name):
    return name in _ENV

def toMagicDict(what):
    return dict(("__%s__" % _name, _value)
        for (_name, _value) in what.iteritems()
    )

def _getIniDefaults():
    return toMagicDict(_ENV)

def readIniFile(filename, env, raw=False):
    if not os.path.isfile(filename):
        raise ValueError("Config %r not found.", filename)
    _magics = _getIniDefaults()
    _magics.update(env)
    if raw:
        _parser = RawConfigParser()
    else:
        _parser = ConfigParser(_magics)
    _parser.read(filename)
    _out = {}
    _sysKeys = [_name.lower() for _name in _magics.keys()]
    for _sect in _parser.sections():
        _out[_sect] = dict(
            (_name, _value)
            for (_name, _value) in _parser.items(_sect)
            if _name not in _sysKeys
        )
    return _out

def readConfigFile(filename, args):
    # Apply config-defined environement variables
    _env = readIniFile(filename, args, raw=True).get("__ENVVARS__", {})
    _env.update(toMagicDict(args))
    return dict((_name, _val)
        for (_name, _val) in readIniFile(filename, _env).iteritems()
        if not (_name.startswith("__") and _name.endswith("__"))
    )

# vim: set sts=4 sw=4 et :
