#! /usr/bin/python3
import paho.mqtt.client as mqtt

class MQTTManager:
    def __init__(self, hostname, broker_port, mqtt_user, mqtt_password, client_id, clean_session) -> None:
        self.hostname = hostname
        self.broker_port = broker_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.client_id = client_id
        self.clean_session = clean_session
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, clean_session=clean_session)

    def __del__(self):
        self._safe_disconnect()
    
    def __str__(self) -> str:
        return f"MQTT connection to host {self.hostname} on port {self.broker_port}, identified as client {self.client_id}. This client is {"NOT " if self.clean_session else str()}persistent."
    
    def __repr__(self) -> str:
        return f"MQTTManager('{self.hostname}', {self.broker_port}, '{self.client_id}', {self.clean_session})"
    
    def _on_pre_connect(self, client, userdata):
        pass

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties):
        pass
    
    def _on_connect_fail(self, client, userdata):
        pass

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        pass

    def _on_log(self, client, userdata, level, buf):
        pass

    def _on_message(self, client, userdata, message):
        pass

    def _on_publish(self, client, userdata, mid, reason_code, properties):
        pass
    
    def _on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        pass

    def _on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        pass

    def _safe_disconnect(self):
        if self.client.is_connected:
            self.client.disconnect()
    
    def publish(self, topic, message, retain):
        try:
            self.client.username_pw_set(self.mqtt_user, self.mqtt_password)

            self.client.connect(self.hostname, self.broker_port)

            self.client.loop_start()

            result = self.client.publish(topic, message, 2, retain)
            result.wait_for_publish()
            status = result[0]
            if status == 0:
                #print(f"Sent `{message}` to topic `{topic}`")
                pass
            else:
                print(f"Failed to send message to topic {topic}")
        finally:
            self._safe_disconnect()
    
    def subscribe(self, topic):
        try:
            self.topic = topic
            
            self.client.username_pw_set(self.mqtt_user, self.mqtt_password)

            self.client.connect(self.hostname, self.broker_port)

            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Stopped by user")
        finally:
            self._safe_disconnect()