"""Main config file."""

def doUnison(system, *args):
    _args = [r"./unison/doSync.py"]
    _args.extend(args)
    _rv = system.shell.execute("python", _args)
    _rc = _rv.wait()
    if _rc not in (0, ):
        raise RuntimeError("Strange Unison return code %r (calling %r)" % (_rc, _args))


def execute(system):
    # Always perform internal folder sync
    doUnison(system, "macbook_internal")
    if "Blue Duck" in system.plugins.airport.SSID:
        _nasIp = system.plugins.samba.getIpFor("eagle-owl")
        doUnison(
            system,
            "macbook_to_nas_local",
            "--arg", "NAS_IP=" + _nasIp
        )

# vim: set sts=4 sw=4 et :
