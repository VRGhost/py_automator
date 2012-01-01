"""file that program starts with."""

if __name__ == "__main__":
    from optparse import OptionParser

    _parser = OptionParser(usage="usage: %prog [options]")
    _parser.add_option("", "--daemon_run",
        action="store_true", dest="is_daemon", default=False,
        help="If given, all stdout and stderr is redirected to "\
         "log file and is shown upon error. "\
         "Ether by growl'ing or in TextEdit.")
    _parser.add_option("", "--console_run",
        action="store_false", dest="is_daemon",
        help="If given, the stdout and stderr are not redirected (default).")

    (options, _) = _parser.parse_args()

    if not options.is_daemon:
        # This could be helpful to someone
        print("**** NON-DAEMON RUN *****")
    # Project imports
    import Application
    Application.Application.consoleRun(options)

# vim: set sts=4 sw=4 et :
