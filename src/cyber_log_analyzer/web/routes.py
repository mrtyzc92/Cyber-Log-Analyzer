from flask import Blueprint


main_blueprint = Blueprint(
    "main",
    __name__,
)


@main_blueprint.get("/")
def index() -> str:
    """Return the application home page."""

    return "Cyber Log Analyzer"
