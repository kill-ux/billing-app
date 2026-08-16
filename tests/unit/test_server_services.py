def test_init_app_services_success(mocker):
    import server

    flask_app = server.app
    mock_db = mocker.Mock()

    mock_thread = mocker.patch("server.threading.Thread")
    mock_thread_instance = mock_thread.return_value

    server.init_app_services(flask_app, mock_db)

    mock_db.create_all.assert_called_once_with()

    mock_thread.assert_called_once_with(
        target=server.consume_and_store_order,
        args=(flask_app, mock_db),
        daemon=True,
    )
    mock_thread_instance.start.assert_called_once_with()


def test_init_app_services_retries_then_succeeds(mocker):
    import server

    flask_app = server.app
    mock_db = mocker.Mock()
    mock_db.create_all.side_effect = [
        RuntimeError("database unavailable"),
        None,
    ]

    mocker.patch("server.threading.Thread")
    mock_sleep = mocker.patch("server.time.sleep")

    server.init_app_services(flask_app, mock_db)

    assert mock_db.create_all.call_count == 2
    mock_sleep.assert_called_once_with(3)