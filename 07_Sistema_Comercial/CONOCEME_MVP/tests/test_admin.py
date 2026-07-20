def _login(client):
    client.get("/admin/login")
    with client.session_transaction() as session:
        token = session["csrf_token"]
    return client.post("/admin/login", data={
        "csrf_token": token, "username": "alex", "password": "test-password",
    })


def _register(client, valid_form):
    response = client.post("/conoceme/inscripcion", data=valid_form)
    return response.location.rsplit("/", 1)[-1]


def test_panel_requires_login(client):
    response = client.get("/admin/registrations")
    assert response.status_code == 302
    assert "/admin/login" in response.location


def test_login_and_panel_access(client):
    response = _login(client)
    assert response.status_code == 302
    assert response.location.endswith("/admin/registrations")
    assert client.get("/admin/registrations").status_code == 200


def test_valid_and_invalid_status_transitions(client, repository, valid_form):
    reference = _register(client, valid_form)
    _login(client)
    with client.session_transaction() as session:
        token = session["csrf_token"]
    response = client.post(f"/admin/registrations/{reference}/status", data={
        "csrf_token": token, "status": "confirmed", "note": "Pago verificado",
    })
    assert response.status_code == 302
    assert repository.by_reference[reference]["status"] == "confirmed"
    assert repository.audit[0]["actor_id"] == "alex"
    detail = client.get(f"/admin/registrations/{reference}")
    assert detail.status_code == 200
    assert "Pago verificado" in detail.get_data(as_text=True)

    response = client.post(f"/admin/registrations/{reference}/status", data={
        "csrf_token": token, "status": "follow_up_sent",
    })
    assert response.status_code == 409


def test_csv_export_contains_only_operational_columns(client, valid_form):
    _register(client, valid_form)
    _login(client)
    response = client.get("/admin/registrations.csv")
    content = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Adulto responsable" in content
    assert "Ana Pérez" in content
    assert "operational_consent" not in content
