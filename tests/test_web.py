from io import BytesIO

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


def test_index_renders_home_page():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<h1>Cyber Log Analyzer</h1>" in html
    assert "<h2>Güvenlik loglarını analiz edin</h2>" in html


def test_index_analyzes_uploaded_log_file():
    app = create_app({"TESTING": True})
    client = app.test_client()

    log_content = (
        b"2026-08-18 09:12:42 | WARNING | "
        b"192.168.1.25 | LOGIN_FAILED | admin\n"
        b"2026-08-18 09:13:01 | WARNING | "
        b"192.168.1.25 | LOGIN_FAILED | admin\n"
        b"2026-08-18 09:13:19 | WARNING | "
        b"192.168.1.25 | LOGIN_FAILED | admin\n"
    )

    response = client.post(
        "/",
        data={
            "threshold": "3",
            "log_file": (
                BytesIO(log_content),
                "sample.log",
            ),
        },
        content_type="multipart/form-data",
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Analiz sonucu" in html
    assert "192.168.1.25: 3 başarısız giriş" in html


def test_index_rejects_unsupported_file_extension():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "threshold": "3",
            "log_file": (
                BytesIO(b"unsupported content"),
                "sample.csv",
            ),
        },
        content_type="multipart/form-data",
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Yalnızca .log veya .txt dosyaları yüklenebilir." in html


def test_index_rejects_invalid_threshold():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "threshold": "0",
            "log_file": (
                BytesIO(b""),
                "sample.log",
            ),
        },
        content_type="multipart/form-data",
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert (
        "Eşik değeri 1 veya daha büyük "
        "bir tam sayı olmalıdır."
    ) in html

def test_index_rejects_missing_log_file():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "threshold": "3",
        },
        content_type="multipart/form-data",
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Lütfen bir log dosyası seçin." in html

def test_index_rejects_malformed_log_content():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "threshold": "3",
            "log_file": (
                BytesIO(b"invalid log line\n"),
                "sample.log",
            ),
        },
        content_type="multipart/form-data",
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert (
        "Log dosyası UTF-8 biçiminde ve "
        "beklenen kayıt yapısında olmalıdır."
    ) in html

def test_index_rejects_file_above_size_limit():
    app = create_app(
        {
            "TESTING": True,
            "MAX_CONTENT_LENGTH": 10,
        }
    )
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "threshold": "3",
            "log_file": (
                BytesIO(b"x" * 100),
                "large.log",
            ),
        },
        content_type="multipart/form-data",
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 413
    assert "<h2>Dosya çok büyük</h2>" in html
    assert "1 MB veya daha küçük bir log dosyası seçin." in html