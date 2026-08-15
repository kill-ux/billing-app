

import time, pika


def test_put_data_on_rabbit_and_check_if_billing_save_it_in_database_successfully(client, app_url):
    payload = {"user_id": 999, "number_of_items": 7, "total_amount": 12.34}

    credentials = pika.PlainCredentials("rabbit", "rabbit")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", port=5672, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(
        queue="rabbit", durable=True, arguments={"x-queue-type": "quorum"}
    )
    channel.basic_publish(
        exchange="",
        routing_key="rabbit",
        body=str(payload)
    )
    connection.close()
    
    time.sleep(1)
    
    resp = client.get(f"{app_url}/api/billing")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    
    matching_orders = [
        item for item in data["data"] if item.get("user_id") == 999
    ]
    assert len(matching_orders) > 0
    assert matching_orders[0]["number_of_items"] == 7
