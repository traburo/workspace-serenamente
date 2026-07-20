import logging
import os

from flask import Flask, render_template

from .config import Config
from .repositories.registrations import PostgresRegistrationRepository
from .routes.public import public_bp
from .routes.admin import admin_bp


def create_app(test_config=None, repository=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    app.extensions["registration_repository"] = (
        repository or PostgresRegistrationRepository(app.config["DATABASE_URL"])
    )
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    @app.after_request
    def secure_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self'; img-src 'self' data:; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'",
        )
        return response

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", message="No encontramos esa página."), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error("Unhandled application error: %s", type(error).__name__)
        return render_template(
            "error.html", message="No pudimos completar la solicitud. Intenta nuevamente."
        ), 500

    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    return app
