def format_security_report(
    suspicious_attempts: dict[str, int],
) -> str:
    """Convert suspicious login results into a readable text report."""

    if not suspicious_attempts:
        return "Şüpheli giriş denemesi bulunamadı."

    lines = ["Şüpheli giriş denemeleri:"]

    for ip_address, count in sorted(suspicious_attempts.items()):
        lines.append(
            f"- {ip_address}: {count} başarısız giriş"
        )

    return "\n".join(lines)