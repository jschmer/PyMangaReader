import logging

log = logging.getLogger('')

def setupLoggerFromCmdArgs(argv):
    # search for --log=LEVEL
    for arg in argv:
        if "--log=" in arg:
            loglevel = arg.replace("--log=", "")
            numeric_level = getattr(logging, loglevel.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % loglevel)
            logging.basicConfig(level=numeric_level)
