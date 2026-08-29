from cyber_log_analyzer.web import create_app


def test_create_app_uses_test_config():
    app = create_app(
        {
            "TESTING": True,
            "MAX_CONTENT_LENGTH": 100,
        }
    )

    assert app.config["TESTING"] is True
    assert app.config["MAX_CONTENT_LENGTH"] == 100


def test_index_returns_application_name():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Cyber Log Analyzer"