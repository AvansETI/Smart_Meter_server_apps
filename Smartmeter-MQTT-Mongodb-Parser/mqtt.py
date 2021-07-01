import paho.mqtt.client as mqtt
from appconfig import AppConfig
from mongo import MongoEngine
from logger import logger
import json

class MQTT(object):

    def __init__(self, config: AppConfig, mongo: MongoEngine):
        self.mqttClient = mqtt.Client("", clean_session=True)
        self.appConfig = config
        self.mongo = mongo

    #
    # Mqtt events
    #
    def on_connect(self, mqttc, obj, flags, rc):
        self.mqttClient.subscribe("smartmeter/raw", 0)
        if rc==0:
            logger.info(msg="MQTT Succesfully connect to broker")
        else:
            logger.info(msg="MQTT connected Error")

    def on_message(self, mqttc, obj, msg):
        try:
            json_payload = json.loads(msg.payload)
            message = self.mongo.save(json_payload)
            logger.debug(msg = json.dumps(json_payload)[0:15])
            self.mqttClient.publish('smartmeter/data',message)
        except Exception as str:
            logger.error(msg= ("Emon.save() exception: {0}", str) )

    def on_publish(self, mqttc, obj, mid):
        pass

    def on_subscribe(self,mqttc, obj, mid, granted_qos):
        pass

    def on_log(self, mqttc, obj, level, msg):
        logger.debug(msg=msg)
        pass

    def on_disconnect(self, mqtt, obj, msg):
        logger.info(msg="MQTT disconnect from broker")

    def run(self):

        # Hook-up all callbacks
        self.mqttClient.on_disconnect = self.on_disconnect
        self.mqttClient.on_message = self.on_message
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_publish = self.on_publish
        self.mqttClient.on_subscribe = self.on_subscribe
        self.mqttClient.on_log = self.on_log

        # Setup mqtt and connect to broker
        self.mqttClient.username_pw_set(username=self.appConfig['mqtt']['username'], password=self.appConfig['mqtt']['password'])
        self.mqttClient.connect(self.appConfig['mqtt']['host'], self.appConfig['mqtt']['port'], 10)

        self.mqttClient.loop_start()

    def isConnected(self):
        return self.mqttClient.is_connected()

    def stop(self):
        self.mqttClient.loop_stop()
        self.mqttClient.disconnect()
