from cyber_log_analyzer.reporters.text_reporter import (
    format_security_report,
)


def test_returns_message_when_result_is_empty():
    result = format_security_report({})

    assert result == "Şüpheli giriş denemesi bulunamadı."


def test_formats_single_suspicious_ip():
    suspicious_attempts = {
        "192.168.1.25": 3,
    }

    result = format_security_report(suspicious_attempts)

    assert result == (
        "Şüpheli giriş denemeleri:\n"
        "- 192.168.1.25: 3 başarısız giriş"
    )


def test_sorts_multiple_ip_addresses():
    suspicious_attempts = {
        "192.168.1.25": 3,
        "10.0.0.8": 4,
    }

    result = format_security_report(suspicious_attempts)

    assert result == (
        "Şüpheli giriş denemeleri:\n"
        "- 10.0.0.8: 4 başarısız giriş\n"
        "- 192.168.1.25: 3 başarısız giriş"
    )