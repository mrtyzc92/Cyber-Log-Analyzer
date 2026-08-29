from cyber_log_analyzer.main import analyze_log_file


def test_analyze_log_file_returns_security_report(tmp_path):
    log_file = tmp_path / "security.log"

    log_file.write_text(
        "\n".join(
            [
                (
                    "2026-08-18 09:10:15 | INFO | "
                    "192.168.1.10 | LOGIN_SUCCESS | mert"
                ),
                (
                    "2026-08-18 09:12:42 | WARNING | "
                    "192.168.1.25 | LOGIN_FAILED | admin"
                ),
                (
                    "2026-08-18 09:13:01 | WARNING | "
                    "192.168.1.25 | LOGIN_FAILED | admin"
                ),
                (
                    "2026-08-18 09:13:19 | WARNING | "
                    "192.168.1.25 | LOGIN_FAILED | admin"
                ),
            ]
        ),
        encoding="utf-8",
    )

    result = analyze_log_file(
        log_file,
        threshold=3,
    )

    assert result == (
        "Şüpheli giriş denemeleri:\n"
        "- 192.168.1.25: 3 başarısız giriş"
    )