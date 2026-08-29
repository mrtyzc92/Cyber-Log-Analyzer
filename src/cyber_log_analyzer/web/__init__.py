from flask import Flask


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

    from cyber_log_analyzer.web.routes import main_blueprint

    app.register_blueprint(main_blueprint)
    return app