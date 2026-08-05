import csv
import io

from flask import (
    Blueprint, Response, current_app, redirect, render_template, request, session,
    url_for,
)

from ..services.security import admin_required, csrf_token, valid_admin_credentials, valid_csrf
from ..services.states import ALLOWED_TRANSITIONS, STATUS_LABELS


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _safe_csv_cell(value):
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if not valid_csrf(request.form.get("csrf_token", "")):
            error = "La sesión venció. Intenta nuevamente."
        elif valid_admin_credentials(
            request.form.get("username", ""), request.form.get("password", "")
        ):
            session.clear()
            session["admin_authenticated"] = True
            session["admin_username"] = current_app.config["ADMIN_USERNAME"]
            csrf_token()
            return redirect(url_for("admin.registrations"))
        else:
            error = "Usuario o contraseña incorrectos."
    return render_template("admin/login.html", error=error, csrf_token=csrf_token())


@admin_bp.post("/logout")
@admin_required
def logout():
    if not valid_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida", 400
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.get("/registrations")
@admin_required
def registrations():
    selected_status = request.args.get("status", "")
    if selected_status not in STATUS_LABELS:
        selected_status = ""
    repository = current_app.extensions["registration_repository"]
    rows = repository.list_registrations(selected_status or None)
    summary = repository.registration_summary()
    return render_template(
        "admin/registrations.html", rows=rows, summary=summary,
        selected_status=selected_status, status_labels=STATUS_LABELS,
        csrf_token=csrf_token(),
    )


@admin_bp.get("/registrations/<public_reference>")
@admin_required
def registration_detail(public_reference):
    repository = current_app.extensions["registration_repository"]
    registration = repository.get_admin(public_reference)
    if not registration:
        return render_template("error.html", message="No encontramos esa inscripción."), 404
    messages = repository.list_messages(public_reference)
    audit_log = repository.list_audit_log(public_reference)
    return render_template(
        "admin/registration_detail.html", registration=registration,
        messages=messages, audit_log=audit_log,
        transitions=ALLOWED_TRANSITIONS.get(registration["status"], set()),
        status_labels=STATUS_LABELS, csrf_token=csrf_token(),
    )


@admin_bp.post("/registrations/<public_reference>/status")
@admin_required
def update_status(public_reference):
    if not valid_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida", 400
    new_status = request.form.get("status", "")
    note = " ".join(request.form.get("note", "").strip().split())[:500] or None
    repository = current_app.extensions["registration_repository"]
    try:
        repository.transition_status(
            public_reference, new_status, session["admin_username"], note
        )
    except ValueError as error:
        return render_template("error.html", message=str(error)), 409
    return redirect(url_for("admin.registration_detail", public_reference=public_reference))


@admin_bp.get("/registrations.csv")
@admin_required
def export_csv():
    selected_status = request.args.get("status")
    if selected_status not in STATUS_LABELS:
        selected_status = None
    repository = current_app.extensions["registration_repository"]
    rows = repository.export_registrations(selected_status)
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([
        "Referencia", "Adulto responsable", "Correo", "WhatsApp",
        "Adolescente", "Edad", "Estado", "Fuente", "Fecha de registro",
    ])
    for row in rows:
        writer.writerow([
            _safe_csv_cell(row["public_reference"]),
            _safe_csv_cell(row["adult_name"]),
            _safe_csv_cell(row["email"]),
            _safe_csv_cell(row["whatsapp"]),
            _safe_csv_cell(row["teen_first_name"]),
            _safe_csv_cell(row["teen_age"]),
            _safe_csv_cell(STATUS_LABELS[row["status"]]),
            _safe_csv_cell(row["source"]),
            _safe_csv_cell(row["created_at"].isoformat()),
        ])
    return Response(
        "\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=conoceme_inscripciones.csv"},
    )
