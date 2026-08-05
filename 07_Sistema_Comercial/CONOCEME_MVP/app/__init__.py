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

    if not app.config["TESTING"] and app.config["APP_ENV"] in {"staging", "production"}:
        required_settings = (
            "SECRET_KEY", "DATABASE_URL", "ADMIN_USERNAME",
            "ADMIN_PASSWORD_HASH", "INTERNAL_JOB_SECRET",
        )
        missing = [name for name in required_settings if not app.config.get(name)]
        if missing:
            raise RuntimeError(
                "Faltan variables obligatorias para un entorno protegido: " + ", ".join(missing)
            )

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
        if app.config["SESSION_COOKIE_SECURE"]:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
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
