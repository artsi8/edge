from paho.mqtt import client as mqtt_client
from app.interfaces.hub_gateway import HubGateway
from app.entities.processed_agent_data import ProcessedAgentData


class HubMqttAdapter(HubGateway):
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.mqtt_client = self._connect_mqtt(broker, port)

    def save_data(self, processed_data: ProcessedAgentData):
        msg = processed_data.model_dump_json()
        result = self.mqtt_client.publish(self.topic, msg)
        if result[0] == 0:
            return True
        else:
            print(f"Message transmission to topic {self.topic} was not successful")
            return False

    @staticmethod
    def _connect_mqtt(broker, port):

        print(f"ATTEMPTING CONNECTION TO {broker}:{port}")

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Successfully established connection with MQTT Broker ({broker}:{port})")
            else:
                print(f"Attempt to connect to {broker}:{port} was unsuccessful. Return code: {rc}\n")
                exit(rc)

        client = mqtt_client.Client()
        client.on_connect = on_connect
        client.connect(broker, port)
        client.loop_start()
        return client

