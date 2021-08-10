import paho.mqtt.client as paho
import random  
import time
from azure.iot.device import IoTHubDeviceClient, Message

broker="192.168.0.199" #IP of your Raspberry Pi
#### this is the device specific key
CONNECTION_STRING = "HostName=FallDetectionSystem.azure-devices.net;DeviceId=primary_one;SharedAccessKey=UZc4N2J6EO2W3JOJ5XG0tHBdZQH3NTFhFCRxOJBaWsM="

MSG_TXT = '{{"is_fall": {is_fall},"heart_rate": {heart_rate}}}'
  
_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
fall = 0
pconnect = True
pdead = 0
pulse = -1
pqueue = []

def iothub_client_message_run(fall,hr):
    # is the fall detected
    is_fall = fall
    # normalised hear range
    heart_rate = hr
    msg_txt_formatted = MSG_TXT.format(is_fall = is_fall, heart_rate = heart_rate)
    message = Message(msg_txt_formatted)
    print( "Sending message: {}".format(message) )
    _client.send_message(message)
    print ( "Message successfully sent" )

#define callback
def on_message(client, userdata, message):
    global pulse
    global pdead
    msg = str(message.payload.decode("utf-8"))
    print("received message =",msg)
    if message.topic == "pulse":
        if float(msg) == -1:
            pconnect = False
            pulse = -1
        elif float(msg) == 0:
            pdead += 1
            if(pdead >= 2):
                pqueue.clear()
                pulse = 0
        else:
            pdead = 0
            pqueue.append(float(msg))
            pconnect = True
    elif message.topic == "fall":
        if len(pqueue)>0:
            pulse = (sum(pqueue)/len(pqueue))
        iothub_client_message_run(1,pulse)
        global fall
        fall += 1

if __name__ == '__main__':
    client= paho.Client("client-001")
    client.on_message=on_message

    print("connecting to broker ",broker)
    client.connect(broker)
    print("subscribing ")
    client.subscribe("fall")
    client.subscribe("pulse")
    last = time.time()
    try:
        while True:
            client.loop()
            if(time.time()-last > 60):
                if(len(pqueue)>0 and pconnect):
                    pulse = (sum(pqueue)/len(pqueue))
                iothub_client_message_run(0,pulse)
                pqueue.clear()
                last = time.time()
    except KeyboardInterrupt:  
        print ( "IoTHubClient sample stopped" )
