def _login(client):
    client.get("/admin/login")
    with client.session_transaction() as session:
        token = session["csrf_token"]
    client.post("/admin/login", data={
        "csrf_token": token, "username": "alex", "password": "test-password",
    })


def _csrf(client):
    with client.session_transaction() as session:
        return session["csrf_token"]


def _campaign(client):
    response = client.post("/admin/content/campaigns/new", data={
        "csrf_token": _csrf(client), "title": "Primera semana",
        "objective": "Crecer la comunidad", "audience": "Mujeres con sobrecarga",
        "theme": "No necesitas sostenerlo todo", "starts_on": "2026-08-10",
        "ends_on": "2026-08-16",
    })
    return response.location.rsplit("/", 1)[-1]


def _piece_form(client, blockers=""):
    return {
        "csrf_token": _csrf(client), "title": "Una pausa también es avanzar",
        "pillar": "Respirar", "format": "Carrusel", "objective": "Generar guardados",
        "cta": "Guárdalo", "caption": "No necesitas sostenerlo todo sin pausa.",
        "script": "", "visual_direction": "Composición clara", "sources": "SER-NM-01",
        "assumptions": "", "approval_pending": "Revisión humana", "blocking_issues": blockers,
    }


def test_content_panel_requires_login(client):
    response = client.get("/admin/content")
    assert response.status_code == 302
    assert "/admin/login" in response.location


def test_create_campaign_and_piece(client, content_repository):
    _login(client)
    campaign_id = _campaign(client)
    response = client.post(f"/admin/content/campaigns/{campaign_id}/pieces",
                           data=_piece_form(client))
    assert response.status_code == 302
    assert len(content_repository.campaigns) == 1
    assert len(content_repository.pieces) == 1
    detail = client.get(response.location)
    assert "Una pausa también es avanzar" in detail.get_data(as_text=True)


def test_generate_weekly_campaign_once(client, content_repository):
    _login(client)
    campaign_id = _campaign(client)
    response = client.post(f"/admin/content/campaigns/{campaign_id}/generate", data={
        "csrf_token": _csrf(client),
    })
    assert response.status_code == 302
    assert len(content_repository.pieces) == 6
    assert {piece["pillar"] for piece in content_repository.pieces.values()} == {
        "Comprender", "Respirar", "Avanzar", "Conectar",
    }
    assert all(piece["blocking_issues"] for piece in content_repository.pieces.values())
    second = client.post(f"/admin/content/campaigns/{campaign_id}/generate", data={
        "csrf_token": _csrf(client),
    })
    assert second.status_code == 409
    assert len(content_repository.pieces) == 6


def test_generate_and_serve_image_asset(client, content_repository):
    _login(client)
    campaign_id = _campaign(client)
    response = client.post(f"/admin/content/campaigns/{campaign_id}/pieces",
                           data=_piece_form(client))
    piece_id = response.location.rsplit("/", 1)[-1]
    response = client.post(f"/admin/content/pieces/{piece_id}/images", data={
        "csrf_token": _csrf(client), "image_prompt": "Imagen editorial sin texto",
    })
    assert response.status_code == 302
    assert len(content_repository.assets) == 1
    asset = next(iter(content_repository.assets.values()))
    image = client.get(f"/admin/content/assets/{asset['id']}")
    assert image.status_code == 200
    assert image.mimetype == "image/png"
    assert image.data == b"fake-png"
    review = client.post(f"/admin/content/assets/{asset['id']}/review", data={
        "csrf_token": _csrf(client), "status": "approved",
    })
    assert review.status_code == 302
    assert asset["status"] == "approved"


def test_build_branded_carousel_from_generated_images(client, content_repository):
    _login(client)
    campaign_id = _campaign(client)
    response = client.post(f"/admin/content/campaigns/{campaign_id}/pieces",
                           data=_piece_form(client))
    piece_id = response.location.rsplit("/", 1)[-1]
    image = BytesIO()
    Image.new("RGB", (800, 1000), "#b8c7bd").save(image, "JPEG")
    for index in range(6):
        asset_id = content_repository.save_image_asset(
            next(iter(content_repository.pieces)), f"Imagen {index}",
            type("Generated", (), {
                "data": image.getvalue(), "mime_type": "image/jpeg", "model": "test-model",
            })(), "alex",
        )
        content_repository.assets[asset_id]["status"] = "approved"

    slide = client.get(f"/admin/content/pieces/{piece_id}/carousel/0.jpg")
    assert slide.status_code == 200
    assert slide.mimetype == "image/jpeg"
    with Image.open(BytesIO(slide.data)) as rendered:
        assert rendered.size == (1080, 1350)

    download = client.get(f"/admin/content/pieces/{piece_id}/carousel.zip")
    assert download.status_code == 200
    assert download.mimetype == "application/zip"
    with ZipFile(BytesIO(download.data)) as archive:
        assert len(archive.namelist()) == 6
        assert archive.namelist()[0] == "serenamente-carrusel-01.jpg"


def test_piece_with_blockers_cannot_be_approved(client, content_repository):
    _login(client)
    campaign_id = _campaign(client)
    response = client.post(f"/admin/content/campaigns/{campaign_id}/pieces",
                           data=_piece_form(client, "Confirmar autorización de imagen"))
    piece_url = response.location
    piece_id = piece_url.rsplit("/", 1)[-1]
    for state in ("in_control", "for_review"):
        response = client.post(f"/admin/content/pieces/{piece_id}/status", data={
            "csrf_token": _csrf(client), "status": state, "comment": "Revisión",
        })
        assert response.status_code == 302
    response = client.post(f"/admin/content/pieces/{piece_id}/status", data={
        "csrf_token": _csrf(client), "status": "approved", "comment": "Aprobar",
    })
    assert response.status_code == 409
    assert next(iter(content_repository.pieces.values()))["status"] == "for_review"


def test_piece_without_blockers_can_be_approved(client, content_repository):
    _login(client)
    campaign_id = _campaign(client)
    response = client.post(f"/admin/content/campaigns/{campaign_id}/pieces",
                           data=_piece_form(client))
    piece_id = response.location.rsplit("/", 1)[-1]
    for state in ("in_control", "for_review", "approved"):
        response = client.post(f"/admin/content/pieces/{piece_id}/status", data={
            "csrf_token": _csrf(client), "status": state, "comment": "Control registrado",
        })
        assert response.status_code == 302
    assert next(iter(content_repository.pieces.values()))["status"] == "approved"
    assert len(content_repository.reviews) == 3
from io import BytesIO
from zipfile import ZipFile

from PIL import Image
