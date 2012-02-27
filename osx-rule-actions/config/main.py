"""Main config file."""

def doUnison(system, *args):
    from unison import doSync

    doSync.run_with_args(args)


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
