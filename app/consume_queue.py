import os
import pika
import json
import time
from pika.exceptions import AMQPConnectionError, AMQPChannelError, StreamLostError
from sqlalchemy.exc import OperationalError

from app.orders import create_order

RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASS')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE')


def process_order_message(ch, method, properties, body, app, db):
    """
    Processes a single RabbitMQ message payload.
    """
    print(f" [.] received: {body.decode()}", flush=True)
    try:
        new_order = json.loads(body.decode())
        
        with app.app_context():
            create_order(db.session, new_order)
            
        print(" [x] created new order", flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except OperationalError as error:
        print(f"DB connection error, requeueing: {error}", flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(5)
    except Exception as error:
        print(f"Failed to process billing message: {error}", flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        time.sleep(5)


def consume_and_store_order(app, db):  
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    
    while True:
        try:
            print(f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}...", flush=True)
            
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    virtual_host='/',
                    credentials=credentials,
                    heartbeat=60 
                )
            )
            channel = connection.channel()
            channel.queue_declare(
                queue=RABBITMQ_QUEUE, 
                durable=True, 
                arguments={"x-queue-type": "quorum"}
            )
            
            callback = lambda ch, method, properties, body: process_order_message(
                ch, method, properties, body, app, db
            )

            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
            print("Successfully connected to RabbitMQ! Waiting for messages...", flush=True)
            
            channel.start_consuming()

        except (AMQPConnectionError, AMQPChannelError, StreamLostError) as e:
            print(f"RabbitMQ connection lost/failed ({e}). Retrying in 5 seconds...", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error in RabbitMQ consumer: {e}. Retrying in 5 seconds...", flush=True)
            time.sleep(5)