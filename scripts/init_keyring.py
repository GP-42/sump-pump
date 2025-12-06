#! /usr/bin/python3

from sump.utilities.keyring import KeyRing

import traceback

if __name__ == "__main__":
    try:
        KeyRing.set_password("MQTTSumpProcessor", "YourPasswordGoesHere")
        KeyRing.set_password("MQTTSumpStatus", "YourPasswordGoesHere")
        KeyRing.set_password("MQTTSumpDBWrite", "YourPasswordGoesHere")
        KeyRing.set_password("MQTTSumpRPi", "YourPasswordGoesHere")
        KeyRing.set_password("MQTTSumpTankWatcher", "YourPasswordGoesHere")
        KeyRing.set_password("MQTTSumpRelay", "YourPasswordGoesHere")
        KeyRing.set_password("MQTTSumpButtons", "YourPasswordGoesHere")
    
    except Exception as e:
        traceback.print_exc()