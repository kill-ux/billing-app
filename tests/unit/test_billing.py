import pytest
import json

def test_process_order_message_success(app, mocker):
    from app.consume_queue import process_order_message

    mock_ch = mocker.Mock()
    mock_method = mocker.Mock(delivery_tag=42)
    mock_db = mocker.Mock()

    mock_create_order = mocker.patch("app.consume_queue.create_order")

    payload = json.dumps({"order_id": 101, "item": "Widget"}).encode("utf-8")

    process_order_message(
        ch=mock_ch,
        method=mock_method,
        properties=None,
        body=payload,
        app=app,
        db=mock_db,
    )
    
    mock_create_order.assert_called_once_with(mock_db.session, {"order_id": 101, "item": "Widget"})
    mock_ch.basic_ack.assert_called_once_with(delivery_tag=42)
    mock_ch.basic_nack.assert_not_called()
    
def test_process_order_message_failure_triggers_nack(app, mocker):
    from app.consume_queue import process_order_message

    mock_ch = mocker.Mock()
    mock_method = mocker.Mock(delivery_tag=42)
    mock_db = mocker.Mock()
    
    mocker.patch("app.consume_queue.create_order", side_effect=Exception("Database error"))
    mocker.patch("time.sleep")

    payload = json.dumps({"order_id": 101}).encode("utf-8")

    process_order_message(
        ch=mock_ch,
        method=mock_method,
        properties=None,
        body=payload,
        app=app,
        db=mock_db
    )

    mock_ch.basic_ack.assert_not_called()
    mock_ch.basic_nack.assert_called_once_with(delivery_tag=42, requeue=False)
    
def test_process_order_message_transient_error_triggers_requeue(app, mocker):
    from app.consume_queue import process_order_message
    from sqlalchemy.exc import OperationalError

    mock_ch = mocker.Mock()
    mock_method = mocker.Mock(delivery_tag=42)
    mock_db = mocker.Mock()
    mocker.patch(
        "app.consume_queue.create_order",
        side_effect=OperationalError("statement", "params", "orig")
    )
    mocker.patch("time.sleep")

    payload = json.dumps({"order_id": 101}).encode("utf-8")

    process_order_message(
        ch=mock_ch,
        method=mock_method,
        properties=None,
        body=payload,
        app=app,
        db=mock_db
    )

    mock_ch.basic_ack.assert_not_called()
    mock_ch.basic_nack.assert_called_once_with(delivery_tag=42, requeue=True)

def test_list_billing_orders(client, mocker):
    from server import Order

    mock_order = mocker.Mock(spec=Order)
    mock_order.id = 1
    mock_order.user_id = 42
    mock_order.number_of_items = 3
    mock_order.total_amount = 99.99

    mock_query = mocker.Mock()
    mock_query.scalars.return_value.all.return_value = [mock_order]

    mocker.patch("server.db.session.execute", return_value=mock_query)

    response = client.get("/api/billing/")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == 1
    assert data["data"][0]["user_id"] == 42

def test_list_billing_orders_db_error(client, mocker):
    mocker.patch("server.db.session.execute", side_effect=Exception("DB error"))

    resp = client.get("/api/billing/")
    
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["status"] == "error"
    assert "DB error" in data["message"]

def test_consume_and_store_order_connection_failure(app, mocker):
    from app.consume_queue import consume_and_store_order

    mocker.patch("pika.BlockingConnection", side_effect=Exception("Connection failed"))
    mock_sleep = mocker.patch("time.sleep", side_effect=KeyboardInterrupt("Stop the loop"))

    with pytest.raises(KeyboardInterrupt, match="Stop the loop"):
        consume_and_store_order(app, mocker.Mock())
    
    mock_sleep.assert_called_once()
