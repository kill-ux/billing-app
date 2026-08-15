

# import time, pika, json


# def test_put_data_on_rabbit_and_check_if_billing_save_it_in_database_successfully(client, app_url):
#     payload = {"user_id": 999, "number_of_items": 7, "total_amount": 12.34}

#     credentials = pika.PlainCredentials("rabbit", "rabbit")
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host="rabbitmq", port=5672, credentials=credentials)
#     )
#     channel = connection.channel()
#     channel.queue_declare(
#         queue="rabbit", durable=True, arguments={"x-queue-type": "quorum"}
#     )
#     body = json.dumps(payload).encode("utf-8")
#     channel.basic_publish(
#         exchange="",
#         routing_key="rabbit",
#         body=body
#     )
#     connection.close()
    
#     time.sleep(1)
    
#     resp = client.get(f"{app_url}/api/billing")
#     assert resp.status_code == 200

#     data = resp.json()
#     assert data["status"] == "success"
    
#     matching_orders = [
#         item for item in data["data"] if item.get("user_id") == 999
#     ]
#     assert len(matching_orders) > 0
#     assert matching_orders[0]["number_of_items"] == 7

import os
import json
import time
import pika


def test_publish_order_to_rabbitmq_saves_to_database(client, app_url):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "rabbit")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "rabbit")
    rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "rabbit")

    payload = {"user_id": 999, "number_of_items": 7, "total_amount": 12.34}

    # 1. Connect and publish
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials
        )
    )
    channel = connection.channel()
    
    # Declare matching quorum queue setup
    channel.queue_declare(
        queue=rabbitmq_queue,
        durable=True,
        arguments={"x-queue-type": "quorum"}
    )

    channel.basic_publish(
        exchange="",
        routing_key=rabbitmq_queue,
        body=json.dumps(payload).encode("utf-8")
    )
    connection.close()

    # 2. Poll the API with retries (up to 5 seconds) to wait for consumer DB write
    matching_orders = []
    max_retries = 10

    for i in range(max_retries):
        print(f"Polling for order in DB, attempt {i + 1}/{max_retries}...")
        time.sleep(0.5)
        resp = client.get(f"{app_url}/api/billing")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                matching_orders = [
                    item for item in data.get("data", []) if item.get("user_id") == 999
                ]
                if matching_orders:
                    break
    

    # 3. Verify order was created in DB
    assert len(matching_orders) > 0, f"Expected order with user_id 999 in DB, but got: {data}"
    assert matching_orders[0]["number_of_items"] == 7
    assert matching_orders[0]["total_amount"] == 12.34