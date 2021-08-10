import random
from random import choices
import time
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=FallDetectionSystem.azure-devices.net;DeviceId=primary_one;SharedAccessKey=UZc4N2J6EO2W3JOJ5XG0tHBdZQH3NTFhFCRxOJBaWsM="

MSG_TXT_ONE = '{{"is_fall": {is_fall},"heart_rate": {heart_rate}}}'
MSG_TXT_TWO = '{{"heart_rate": {heart_rate}}}'

def iothub_client_init():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def iothub_client_telemetry_sample_run():

    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        while True:
            heart_rate_one = random.randint(50,100)
            heart_rate_two = -1
            population = [heart_rate_one, heart_rate_two]
            weights = [0.70,0.30]
            heart_rate = choices(population, weights)

            population = [0,1]
            weights = [0.7,0.3]
            flag = choices(population, weights)

            if flag[0]:
                msg_txt_formatted = MSG_TXT_TWO.format(heart_rate = heart_rate[0])
            else:
                msg_txt_formatted = MSG_TXT_ONE.format(is_fall = 1, heart_rate = heart_rate[0])

            message = Message(msg_txt_formatted)

            print( "Sending message: {}".format(message) )
            client.send_message(message)
            print ( "Message successfully sent" )
            
            sleep_time = random.randint(10, 100)
            time.sleep(20)

    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
    print ( "IoT Hub - Simulated device" )
    print ( "Press Ctrl-C to exit" )
    iothub_client_telemetry_sample_run()