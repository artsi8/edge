from app.interfaces.hub_gateway import HubGateway
import paho.mqtt.client as mqtt

from app.entities.agent_data import AgentData
import logging

from app.usecases.data_processing import process_agent_data
from app.interfaces.agent_gateway import AgentGateway


class AgentMQTTAdapter(AgentGateway):
    def __init__(
        self,
        broker_host,
        broker_port,
        topic,
        hub_gateway: HubGateway,
        batch_size=7,
    ):

        self.batch_size = batch_size

        # Ініціалізуємо клієнта MQTT
        self.client = mqtt.Client()

        # Встановлюємо хост MQTT брокера
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic

        # Ініціалізуємо шлюз хаба
        self.hub_gateway = hub_gateway

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Successfully connected to MQTT broker")
            self.client.subscribe(self.topic)
        else:
            logging.info(f"Connection to MQTT broker failed with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Processing agent data and sent it to hub gateway"""
        try:
            payload: str = msg.payload.decode("utf-8")
            agent_data = AgentData.model_validate_json(payload, strict=True)
            processed_data = process_agent_data(agent_data)

            # Зберігаємо оброблені дані в хабі
            if not self.hub_gateway.save_data(processed_data):
                logging.error("Hub is currently UNavailable")
        except Exception as e:
            logging.info(f"An error occurred while processing MQTT message: {e}")

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_host, self.broker_port, 60)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()