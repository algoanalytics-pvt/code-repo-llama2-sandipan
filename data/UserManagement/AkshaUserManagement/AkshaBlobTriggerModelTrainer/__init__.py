import logging
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

import azure.functions as func


NAMESPACE_CONNECTION_STR = "Endpoint=sb://akshamodeltrainerqueue.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=uV6S2PCkenwicBgpdwLSqnFA14BBY2D9t+ASbE+6a84="
QUEUE_NAME = "model-trainer"

async def send_single_message(sender):
    # Create a Service Bus message and send it to the queue
    message = ServiceBusMessage("Start Model Training")
    await sender.send_messages(message)
    print("Sent a single message")


async def sendrun():
    # create a Service Bus client using the connection string
    async with ServiceBusClient.from_connection_string(
        conn_str=NAMESPACE_CONNECTION_STR,
        logging_enable=True) as servicebus_client:
        # Get a Queue Sender object to send messages to the queue
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            # Send one message
            await send_single_message(sender)
     

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    asyncio.run(sendrun())
    print("Done sending messages")
