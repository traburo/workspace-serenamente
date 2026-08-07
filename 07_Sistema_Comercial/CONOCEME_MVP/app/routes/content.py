from datetime import date
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from flask import Blueprint, Response, current_app, redirect, render_template, request, session, url_for

from ..services.content_states import CONTENT_STATUS_LABELS, CONTENT_TRANSITIONS
from ..services.content_generation import WeeklyContentGenerator
from ..services.carousel_rendering import carousel_copy, render_carousel_slide
from ..services.image_generation import ImageGenerationError, compose_image_prompt
from ..services.security import admin_required, csrf_token, valid_csrf


content_bp = Blueprint("content", __name__, url_prefix="/admin/content")
PILLARS = ("Comprender", "Respirar", "Avanzar", "Conectar")
FORMATS = ("Carrusel", "Reel", "Publicación", "Historias")


def _repo():
    return current_app.extensions["content_repository"]


def _clean(value, limit=4000):
    return request.form.get(value, "").strip()[:limit]


def _carousel_assets(piece_id):
    assets = [asset for asset in _repo().list_image_assets(piece_id)
              if asset["status"] != "rejected"]
    return list(reversed(assets[:6]))


def _render_slide(piece, assets, index):
    if not assets:
        raise ValueError("Genera al menos una imagen antes de componer el carrusel.")
    asset = _repo().get_image_asset(assets[index % len(assets)]["id"])
    logo_path = Path(current_app.static_folder) / "brand" / "logo-serenamente.webp"
    return render_carousel_slide(
        asset["content"], carousel_copy(piece)[index], index, logo_path.read_bytes()
    )


def _piece_form():
    blockers = [line.strip() for line in _clean("blocking_issues", 2000).splitlines() if line.strip()]
    return {
        "title": _clean("title", 160), "pillar": _clean("pillar", 40),
        "format": _clean("format", 40), "scheduled_for": _clean("scheduled_for", 30),
        "objective": _clean("objective"), "cta": _clean("cta", 500),
        "caption": _clean("caption", 12000), "script": _clean("script", 12000),
        "visual_direction": _clean("visual_direction", 8000),
        "sources": _clean("sources", 8000), "assumptions": _clean("assumptions", 8000),
        "approval_pending": _clean("approval_pending", 8000), "blocking_issues": blockers,
    }


@content_bp.get("")
@admin_required
def campaigns():
    return render_template(
        "admin/content/campaigns.html", campaigns=_repo().list_campaigns(),
        csrf_token=csrf_token(),
    )


@content_bp.route("/campaigns/new", methods=["GET", "POST"])
@admin_required
def new_campaign():
    error = None
    if request.method == "POST":
        if not valid_csrf(request.form.get("csrf_token", "")):
            return "Solicitud inválida", 400
        data = {name: _clean(name, 500) for name in
                ("title", "objective", "audience", "theme", "starts_on", "ends_on")}
        if not all(data.values()):
            error = "Completa todos los campos del brief inicial."
        elif data["ends_on"] < data["starts_on"]:
            error = "La fecha final no puede ser anterior al inicio."
        else:
            campaign_id = _repo().create_campaign(data, session["admin_username"])
            return redirect(url_for("content.campaign_detail", campaign_id=campaign_id))
    return render_template(
        "admin/content/campaign_form.html", error=error, today=date.today().isoformat(),
        csrf_token=csrf_token(),
    )


@content_bp.get("/campaigns/<uuid:campaign_id>")
@admin_required
def campaign_detail(campaign_id):
    campaign = _repo().get_campaign(campaign_id)
    if not campaign:
        return render_template("error.html", message="No encontramos esa campaña."), 404
    return render_template(
        "admin/content/campaign_detail.html", campaign=campaign,
        pieces=_repo().list_pieces(campaign_id), status_labels=CONTENT_STATUS_LABELS,
        pillars=PILLARS, formats=FORMATS, csrf_token=csrf_token(),
    )


@content_bp.post("/campaigns/<uuid:campaign_id>/generate")
@admin_required
def generate_campaign(campaign_id):
    if not valid_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida", 400
    campaign = _repo().get_campaign(campaign_id)
    if not campaign:
        return render_template("error.html", message="No encontramos esa campaña."), 404
    pieces = WeeklyContentGenerator().generate(campaign)
    try:
        _repo().create_generated_pieces(campaign_id, pieces, session["admin_username"])
    except ValueError as error:
        return render_template("error.html", message=str(error)), 409
    return redirect(url_for("content.campaign_detail", campaign_id=campaign_id))


@content_bp.post("/campaigns/<uuid:campaign_id>/pieces")
@admin_required
def create_piece(campaign_id):
    if not valid_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida", 400
    data = _piece_form()
    if not data["title"] or data["pillar"] not in PILLARS or data["format"] not in FORMATS:
        return render_template("error.html", message="La pieza necesita título, pilar y formato válidos."), 400
    piece_id = _repo().create_piece(campaign_id, data, session["admin_username"])
    return redirect(url_for("content.piece_detail", piece_id=piece_id))


@content_bp.route("/pieces/<uuid:piece_id>", methods=["GET", "POST"])
@admin_required
def piece_detail(piece_id):
    if request.method == "POST":
        if not valid_csrf(request.form.get("csrf_token", "")):
            return "Solicitud inválida", 400
        data = _piece_form()
        if not data["title"] or data["pillar"] not in PILLARS or data["format"] not in FORMATS:
            return render_template("error.html", message="La pieza necesita título, pilar y formato válidos."), 400
        try:
            _repo().update_piece(piece_id, data)
        except ValueError as error:
            return render_template("error.html", message=str(error)), 409
        return redirect(url_for("content.piece_detail", piece_id=piece_id))
    piece = _repo().get_piece(piece_id)
    if not piece:
        return render_template("error.html", message="No encontramos esa pieza."), 404
    image_assets = _repo().list_image_assets(piece_id)
    return render_template(
        "admin/content/piece_detail.html", piece=piece, reviews=_repo().list_reviews(piece_id),
        image_assets=image_assets,
        suggested_image_prompt=compose_image_prompt(piece),
        image_generation_configured=current_app.extensions["content_image_service"].configured,
        carousel_ready=piece["format"] == "Carrusel" and bool(image_assets),
        transitions=CONTENT_TRANSITIONS.get(piece["status"], set()),
        status_labels=CONTENT_STATUS_LABELS, pillars=PILLARS, formats=FORMATS,
        csrf_token=csrf_token(),
    )


@content_bp.post("/pieces/<uuid:piece_id>/images")
@admin_required
def generate_piece_image(piece_id):
    if not valid_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida", 400
    piece = _repo().get_piece(piece_id)
    if not piece:
        return render_template("error.html", message="No encontramos esa pieza."), 404
    prompt = _clean("image_prompt", 8000) or compose_image_prompt(piece)
    try:
        generated = current_app.extensions["content_image_service"].generate(prompt)
        _repo().save_image_asset(piece_id, prompt, generated, session["admin_username"])
    except (ImageGenerationError, ValueError) as error:
        return render_template("error.html", message=str(error)), 502
    return redirect(url_for("content.piece_detail", piece_id=piece_id))


@content_bp.get("/pieces/<uuid:piece_id>/carousel/<int:index>.jpg")
@admin_required
def carousel_slide(piece_id, index):
    piece = _repo().get_piece(piece_id)
    if not piece or piece["format"] != "Carrusel" or index not in range(6):
        return "Lámina no encontrada", 404
    try:
        content = _render_slide(piece, _carousel_assets(piece_id), index)
    except ValueError as error:
        return render_template("error.html", message=str(error)), 409
    return Response(content, mimetype="image/jpeg", headers={
        "Cache-Control": "private, no-store", "Content-Disposition": "inline",
    })


@content_bp.get("/pieces/<uuid:piece_id>/carousel.zip")
@admin_required
def download_carousel(piece_id):
    piece = _repo().get_piece(piece_id)
    if not piece or piece["format"] != "Carrusel":
        return "Carrusel no encontrado", 404
    assets = _carousel_assets(piece_id)
    if not assets:
        return render_template("error.html", message="Genera al menos una imagen antes de componer el carrusel."), 409
    archive = BytesIO()
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        for index in range(6):
            bundle.writestr(f"serenamente-carrusel-{index + 1:02d}.jpg",
                            _render_slide(piece, assets, index))
    return Response(archive.getvalue(), mimetype="application/zip", headers={
        "Content-Disposition": "attachment; filename=serenamente-carrusel.zip",
        "Cache-Control": "private, no-store",
    })


@content_bp.get("/assets/<uuid:asset_id>")
@admin_required
def image_asset(asset_id):
    asset = _repo().get_image_asset(asset_id)
    if not asset:
        return "Imagen no encontrada", 404
    return Response(asset["content"], mimetype=asset["mime_type"], headers={
        "Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff",
    })


@content_bp.post("/assets/<uuid:asset_id>/review")
@admin_required
def review_image_asset(asset_id):
    if not valid_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida", 400
    try:
        piece_id = _repo().review_image_asset(
            asset_id, _clean("status", 30), session["admin_username"]
        )
    except ValueError as error:
        return render_template("error.html", message=str(error)), 409
    return redirect(url_for("content.piece_detail", piece_id=piece_id))


@content_bp.post("/pieces/<uuid:piece_id>/status")
@admin_required
def transition_piece(piece_id):
    if not valid_csrf(request.form.get("csrf_token", "")):
        return "Solicitud inválida", 400
    try:
        _repo().transition_piece(
            piece_id, _clean("status", 40), session["admin_username"], _clean("comment", 1000) or None
        )
    except ValueError as error:
        return render_template("error.html", message=str(error)), 409
    return redirect(url_for("content.piece_detail", piece_id=piece_id))
