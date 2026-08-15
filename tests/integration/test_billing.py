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

    # 2. Dynamic polling (retries every 0.5s up to 5s max)
    matching_orders = []
    max_retries = 10

    for _ in range(max_retries):
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

    # 3. Comprehensive assertions
    assert len(matching_orders) > 0, "Order was not found in DB after queue consumption"
    assert matching_orders[0]["number_of_items"] == 7
    assert matching_orders[0]["total_amount"] == 12.34