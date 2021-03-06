==============
tank-control
==============

--------------------------------------
Tank daemon start/stop/reload helper
--------------------------------------

SYNOPSIS
========

  tank-control [options] <SERVER> <COMMAND> [CONFPATH]

Where <SERVER> is one of:

    all, api, registry, scrubber

And command is one of:

    start, stop, shutdown, restart, reload, force-reload

And CONFPATH is the optional configuration file to use.

OPTIONS
=======

  **--version**
        show program's version number and exit

  **-h, --help**
        show this help message and exit

  **--config-file=PATH**
        Path to a config file to use. Multiple config files
        can be specified, with values in later files taking
        precedence. The default files used are: []

  **-d, --debug**
        Print debugging output

  **--nodebug**
        Do not print debugging output

  **-v, --verbose**
        Print more verbose output

  **--noverbose**
        Do not print more verbose output

  **--log-config=PATH**
        If this option is specified, the logging configuration
        file specified is used and overrides any other logging
        options specified. Please see the Python logging
        module documentation for details on logging
        configuration files.

  **--log-format=FORMAT**
        A logging.Formatter log message format string which
        may use any of the available logging.LogRecord
        attributes. Default: none

  **--log-date-format=DATE_FORMAT**
        Format string for %(asctime)s in log records. Default: none

  **--log-file=PATH**
        (Optional) Name of log file to output to. If not set,
        logging will go to stdout.

  **--log-dir=LOG_DIR**
        (Optional) The directory to keep log files in (will be
        prepended to --logfile)

  **--use-syslog**
        Use syslog for logging.

  **--nouse-syslog**
        Do not use syslog for logging.

  **--syslog-log-facility=SYSLOG_LOG_FACILITY**
        syslog facility to receive log lines

  **--pid-file=PATH**
        File to use as pid file. Default:
        /var/run/tank/$server.pid

SEE ALSO
========

* `X7 Tank <http://tank.x7.org>`__

BUGS
====

* Tank is sourced in Launchpad so you can view current bugs at `X7 Tank <http://tank.x7.org>`__
