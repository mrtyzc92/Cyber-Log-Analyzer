from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Blueprint, render_template, request

from cyber_log_analyzer.agents.security_log_workflow import (
    run_security_log_agent,
)
from cyber_log_analyzer.agents.state import AgentStatus


main_blueprint = Blueprint(
    "main",
    __name__,
)


@main_blueprint.route("/", methods=["GET", "POST"])
def index() -> str:
    """Render the home page and process uploaded log files."""

    report: str | None = None
    error: str | None = None
    agent_step_count: int | None = None
    threshold = 3

    if request.method == "POST":
        uploaded_file = request.files.get("log_file")
        threshold_text = request.form.get("threshold", "3")

        try:
            threshold = int(threshold_text)

            if threshold < 1:
                raise ValueError
        except ValueError:
            error = (
                "Eşik değeri 1 veya daha büyük "
                "bir tam sayı olmalıdır."
            )

        if error is None:
            if uploaded_file is None or uploaded_file.filename == "":
                error = "Lütfen bir log dosyası seçin."
            elif Path(uploaded_file.filename).suffix.lower() not in {
                ".log",
                ".txt",
            }:
                error = "Yalnızca .log veya .txt dosyaları yüklenebilir."
            else:
                with TemporaryDirectory() as temp_directory:
                    log_path = Path(temp_directory) / "uploaded.log"
                    uploaded_file.save(log_path)

                    state = run_security_log_agent(
                        log_path,
                        threshold=threshold,
                    )

                    if state.status is AgentStatus.COMPLETED:
                        report = state.result
                        agent_step_count = state.current_step
                    else:
                        error = (
                            "Log dosyası UTF-8 biçiminde ve "
                            "beklenen kayıt yapısında olmalıdır."
                        )

    return render_template(
        "index.html",
        report=report,
        error=error,
        threshold=threshold,
        agent_step_count=agent_step_count,
    )
