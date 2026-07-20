import secrets
from functools import wraps

from flask import current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def valid_csrf(value):
    expected = session.get("csrf_token", "")
    return bool(expected and value and secrets.compare_digest(expected, value))


def valid_admin_credentials(username, password):
    configured_username = current_app.config["ADMIN_USERNAME"]
    configured_hash = current_app.config["ADMIN_PASSWORD_HASH"]
    if not configured_username or not configured_hash:
        return False
    return secrets.compare_digest(username, configured_username) and check_password_hash(
        configured_hash, password
    )


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("admin.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped
