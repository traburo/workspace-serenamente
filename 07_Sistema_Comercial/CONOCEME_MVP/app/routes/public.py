import time

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from ..services.validation import validate_registration
from ..services.security import csrf_token, valid_csrf


public_bp = Blueprint("public", __name__)
EVENT_SLUG = "conoceme-2026-10-01"


def _form_context(values=None, errors=None):
    return {
        "csrf_token": csrf_token(),
        "values": values or {},
        "errors": errors or {},
        "whatsapp": current_app.config["CONTACT_WHATSAPP"],
        "staging_mode": current_app.config["STAGING_MODE"],
    }


@public_bp.get("/")
def index():
    return redirect(url_for("public.conoceme"))


@public_bp.get("/conoceme")
def conoceme():
    session["form_started_at"] = int(time.time())
    return render_template("conoceme.html", **_form_context())


@public_bp.post("/conoceme/inscripcion")
def register():
    values = request.form.to_dict()
    errors, data = validate_registration(values)

    if not valid_csrf(values.get("csrf_token", "")):
        errors["form"] = "La sesión del formulario venció. Recarga la página e intenta nuevamente."
    if values.get("website"):
        errors["form"] = "No pudimos procesar la solicitud."
    started_at = session.get("form_started_at", 0)
    if not current_app.config["TESTING"] and time.time() - started_at < 1:
        errors["form"] = "Espera un momento y vuelve a enviar el formulario."

    if errors:
        return render_template(
            "conoceme.html", **_form_context(values=values, errors=errors)
        ), 422

    repository = current_app.extensions["registration_repository"]
    result = repository.register(
        EVENT_SLUG, data, allow_draft=current_app.config["STAGING_MODE"]
    )
    session.pop("form_started_at", None)
    return redirect(url_for("public.registration_result", public_reference=result.public_reference))


@public_bp.get("/inscripcion/<public_reference>")
def registration_result(public_reference):
    repository = current_app.extensions["registration_repository"]
    registration = repository.get_public(public_reference)
    if not registration:
        return render_template("error.html", message="No encontramos esa inscripción."), 404
    return render_template(
        "registration_result.html",
        registration=registration,
        whatsapp=current_app.config["CONTACT_WHATSAPP"],
        staging_mode=current_app.config["STAGING_MODE"],
    )


@public_bp.get("/health")
def health():
    repository = current_app.extensions["registration_repository"]
    try:
        repository.healthcheck()
    except Exception:
        return {"status": "unavailable"}, 503
    return {"status": "ok"}
