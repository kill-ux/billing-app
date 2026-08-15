

import time, pika, json, os


def test_put_data_on_rabbit_and_check_if_billing_save_it_in_database_successfully(client, app_url):
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
    
    time.sleep(3)
    
    resp = client.get(f"{app_url}/api/billing")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    
    matching_orders = [
        item for item in data["data"] if item.get("user_id") == 999
    ]
    assert len(matching_orders) > 0
    assert matching_orders[0]["number_of_items"] == 7

