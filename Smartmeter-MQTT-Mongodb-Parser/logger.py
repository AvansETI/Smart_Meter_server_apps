import logging

# Setup logger
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(levelname)-8s %(thread)d %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("mqtt2mongo")
logger.setLevel(logging.INFO)

class Logger(object):
    def __init__(self):
        pass

    def log(self):
        return logger
