from datetime import datetime, timezone
from pymongo import monitoring
from mongoengine import *
from dsmr import *
from appconfig import AppConfig
from logger import logger
from typing import List
import threading
from bson import json_util
import json


class CommandLogger(monitoring.CommandListener):
    def started(self, event):
        logger.debug("Command {0.command_name} with request id "
                 "{0.request_id} started on server "
                 "{0.connection_id}".format(event))

    def succeeded(self, event):
        logger.debug("Command {0.command_name} with request id "
                 "{0.request_id} on server {0.connection_id} "
                 "succeeded in {0.duration_micros} "
                 "microseconds".format(event))

    def failed(self, event):
        logger.debug("Command {0.command_name} with request id "
                 "{0.request_id} on server {0.connection_id} "
                 "failed in {0.duration_micros} "
                 "microseconds".format(event))

# Mongodb schema
class SmartMeterDataRaw(Document):
    p1 = StringField(required = True, max_length = 2048)
    p1_decoded = DictField(required = False, max_length = 2048)
    signature = StringField(required = True, max_length = 128)
    s0 = DictField(required = False, max_length=1024)
    s1 = DictField(required = False, max_length=1024)
    aware_local_now = datetime.now(timezone.utc).astimezone()
    createdAt = DateTimeField(required = True, default = aware_local_now)
    print(aware_local_now)

class SmartMeterDataDecoded(Document):
    signature = StringField(required = True, max_length = 128)
    p1_decoded = DictField(required = False, max_length = 2048)
    s0 = DictField(required = False, max_length=1024)
    s1 = DictField(required = False, max_length=1024)
    aware_local_now = datetime.now(timezone.utc).astimezone()
    createdAt = DateTimeField(required = True, default = aware_local_now)
    print(aware_local_now)

class MongoEngine(object):
    def __init__(self, config: AppConfig):

        monitoring.register(CommandLogger())

        database = config['mongodb']['database']
        host = config['mongodb']['host']
        port = config['mongodb']['port']
        connect(db = database, host = host, port = port )

        self.queue: List[SmartMeterDataRaw] = list()
        self.decodedqueue: List[SmartMeterDataDecoded] = list()

    def _store_thread(self, emon: SmartMeterDataRaw, emon2: SmartMeterDataDecoded):
        try:
            SmartMeterDataRaw.objects.insert(self.queue, load_bulk=False)
            self.queue.clear()
            SmartMeterDataDecoded.objects.insert(self.decodedqueue, load_bulk=False)
            self.decodedqueue.clear()
            logger.debug(msg="Emon.save() succesfull")
        except Exception as e:
            logger.error(msg=("Emon.save() exception: {0}", str(e)))

    def save(self, json_payload):

        try:
            self.emon = SmartMeterDataRaw(
                p1 = json_payload['datagram']['p1'],
                signature = json_payload['datagram']['signature'],
                s0 = json_payload['datagram']['s0'],
                s1 = json_payload['datagram']['s1']
            )
            #Parse P1 message
            self.emon.p1_decoded = DSMR_Parser(self.emon.p1).parse()
            # Save to db
            #self.emon.save()
            self.decoded = SmartMeterDataDecoded(
                p1_decoded = self.emon.p1_decoded,
                signature = json_payload['datagram']['signature'],
                s0 = json_payload['datagram']['s0'],
                s1 = json_payload['datagram']['s1']
            )
            self.decodedqueue.append(self.decoded)

            # Queue multiple documents and try to save
            self.queue.append(self.emon)
            thread = threading.Thread(target=self._store_thread, args=(self.queue, self.decodedqueue, ))
            thread.daemon = True
            thread.start()
            return self.decoded.to_json()

        except Exception as str:
            logger.error(msg=("Emon.save() exception: {0}", str))

