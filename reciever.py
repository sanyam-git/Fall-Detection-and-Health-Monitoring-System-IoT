import requests
from azure.eventhub import TransportType
from azure.eventhub import EventHubConsumerClient

EVENTHUB_COMPATIBLE_ENDPOINT = "sb://ihsuprodpnres008dednamespace.servicebus.windows.net/"

EVENTHUB_COMPATIBLE_PATH = "iothub-ehub-falldetect-8868286-a2836f4b87"

IOTHUB_SAS_KEY = "n38ZujjjBBKSnBr+ApNpI4kqK6LVXScPsUarCEvSO20="

CONNECTION_STR = f'Endpoint={EVENTHUB_COMPATIBLE_ENDPOINT}/;SharedAccessKeyName=service;SharedAccessKey={IOTHUB_SAS_KEY};EntityPath={EVENTHUB_COMPATIBLE_PATH}'

# reciever first needed to verify on Twilio

# make this true  to start sending alert messages
SEND_SMS = 1
SMS_RECIEVER = '+919136702250'
SMS_SENDER = '+14697323891'

LOCAL = False

POST_URL = 'https://hesoyam.pythonanywhere.com/db_update'

if LOCAL:
    POST_URL = 'http://127.0.0.1:5000/db_update'

def send_request(message, properties):
    url = POST_URL
    # extracting message
    is_fall = 0
    if 'is_fall' not in message:
        is_fall = 0
    else:
        is_fall = message['is_fall']
    heart_rate = message['heart_rate']

    # extracting time and device id
    device_id_key = b'iothub-connection-device-id'
    timestamp_key = b'iothub-enqueuedtime'

    device_id = (properties[device_id_key]).decode('utf-8')
    timestamp = int(properties[timestamp_key]/1000) # converting from ms to s and float-> int

    payload = {'is_sms':SEND_SMS,'sms_sender':SMS_SENDER,'sms_reciever':SMS_RECIEVER,\
            'is_fall': is_fall, 'timestamp' : timestamp,'device_id': device_id,'heart_rate': heart_rate}
    requests.post(url, data = payload)
    print("requests sent")

def on_event_batch(partition_context, events):
    for event in events:
        print("Message receiving :")
        print(event.body_as_json())
        print("\n")
        send_request(event.body_as_json(), event.system_properties)

def on_error(partition_context, error):
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))


def main():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
    )
    try:
        with client:
            client.receive_batch(
                on_event_batch=on_event_batch,
                on_error=on_error
            )
    except KeyboardInterrupt:
        print("Receiving has stopped.")

if __name__ == '__main__':
    print("Connected : Waiting for messages :")
    main()
