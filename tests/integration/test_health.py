import os
from time import time

import pika

def test_health_endpoint(client, app_url):
    resp = client.get(f"{app_url}/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "services": {"database": "up"}}

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

# def test_create_movie(client, app_url):
#     movie_data = {"title": "Test Movie", "description": "A test movie description"}
#     resp = client.post(f"{app_url}/api/movies", json=movie_data)
#     assert resp.status_code == 201
#     assert resp.json()["title"] == movie_data["title"]
#     assert resp.json()["description"] == movie_data["description"]

# def test_list_movies(client, app_url):
#     resp = client.get(f"{app_url}/api/movies")
#     movie_data = {
#         "description": "A test movie description",
#         "title": "Test Movie",
#     }
#     assert resp.status_code == 200
#     res = resp.json()
#     assert res[0]["title"] == movie_data["title"]
#     assert res[0]["id"] is not None
#     assert len(res) == 1
