#!/usr/bin/python3
import time
import os, signal, sys
import logging

from appconfig import AppConfig
from mongo import MongoEngine
from mqtt import MQTT

# Setup logger
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(levelname)-8s %(thread)d %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("mqtt2mongo")
logger.setLevel(logging.INFO)

appconfig = AppConfig()
mongo = MongoEngine(config = appconfig)
mqtt = MQTT(config = appconfig, mongo = mongo)

def run_program():
    while True:
       if not mqtt.isConnected():
           try:
               mqtt.run()
           except:
                logging.info(msg="Cant't connect to Broker, retry in 30 seconds")
       time.sleep(1.0)
       pass

def keyboardInterruptHandler(signal, frame):
    logging.info(msg = "KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    mqtt.stop()
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    run_program()