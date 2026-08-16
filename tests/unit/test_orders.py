import pytest
from app.orders import Order, create_order

def test_order_constructor():
    order = Order(
        user_id=10,
        number_of_items=2,
        total_amount=49.99,
    )

    assert order.user_id == 10
    assert order.number_of_items == 2
    assert order.total_amount == 49.99
    
def test_create_order_success(mocker):
    session = mocker.Mock()

    payload = {
        "user_id": 10,
        "number_of_items": 2,
        "total_amount": 49.99,
    }

    create_order(session, payload)

    added_order = session.add.call_args.args[0]

    assert isinstance(added_order, Order)
    assert added_order.user_id == 10
    assert added_order.number_of_items == 2
    assert added_order.total_amount == 49.99

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.rollback.assert_not_called()
    
def test_create_order_rolls_back_and_raises(mocker):
    session = mocker.Mock()
    session.commit.side_effect = RuntimeError("commit failed")

    payload = {
        "user_id": 10,
        "number_of_items": 2,
        "total_amount": 49.99,
    }

    with pytest.raises(Exception, match="commit failed"):
        create_order(session, payload)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.rollback.assert_called_once()
    
def test_create_order_missing_field_rolls_back(mocker):
    session = mocker.Mock()

    payload = {
        "user_id": 10,
        "number_of_items": 2,
    }

    with pytest.raises(Exception, match="total_amount"):
        create_order(session, payload)

    session.rollback.assert_called_once()
    session.commit.assert_not_called()