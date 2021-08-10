from azure.eventhub import TransportType
from azure.eventhub import EventHubConsumerClient
from utils import save_to_db, check_for_alert
import sqlite3
import os.path

EVENTHUB_COMPATIBLE_ENDPOINT = "sb://ihsuprodpnres008dednamespace.servicebus.windows.net/"

EVENTHUB_COMPATIBLE_PATH = "iothub-ehub-falldetect-8868286-a2836f4b87"

IOTHUB_SAS_KEY = "n38ZujjjBBKSnBr+ApNpI4kqK6LVXScPsUarCEvSO20="

CONNECTION_STR = f'Endpoint={EVENTHUB_COMPATIBLE_ENDPOINT}/;SharedAccessKeyName=service;SharedAccessKey={IOTHUB_SAS_KEY};EntityPath={EVENTHUB_COMPATIBLE_PATH}'

# reciever first needed to verify on Twilio

# make this true  to start sending alert messages
SEND_SMS = False
SMS_RECIEVER = '+919783760254'
SMS_SENDER = '+14697323891'

db_name = 'main_db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, db_name)
conn = sqlite3.connect(db_path)

def on_event_batch(partition_context, events):
    for event in events:
        print("Message receiving :")
        print(event.body_as_json())
        print("\n")
        if SEND_SMS:
            is_alert = check_for_alert(event.body_as_json(),event.system_properties,SMS_SENDER,SMS_RECIEVER)
        save_to_db(conn, event.body_as_json(),event.system_properties)

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