from flask import Flask, render_template
from werkzeug.exceptions import RequestEntityTooLarge


def create_app(
    test_config: dict[str, object] | None = None,
) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    app.config.from_mapping(
        MAX_CONTENT_LENGTH=1 * 1024 * 1024,
    )

    if test_config is not None:
        app.config.update(test_config)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(
        _error: RequestEntityTooLarge,
    ) -> tuple[str, int]:
        """Render a user-friendly response for oversized uploads."""

        return render_template("413.html"), 413

    from cyber_log_analyzer.web.routes import main_blueprint

    app.register_blueprint(main_blueprint)

    return app