def test_valid_registration_redirects_and_normalizes(client, repository, valid_form):
    response = client.post("/conoceme/inscripcion", data=valid_form)
    assert response.status_code == 302
    assert "ana@example.com" in repository.by_email


def test_invalid_data_is_rejected(client, valid_form):
    valid_form.update(email="not-an-email", teen_age="10", phone="123")
    response = client.post("/conoceme/inscripcion", data=valid_form)
    assert response.status_code == 422
    assert "correo válido" in response.get_data(as_text=True)


def test_duplicate_registration_reuses_reference(client, repository, valid_form):
    first = client.post("/conoceme/inscripcion", data=valid_form)
    client.get("/conoceme")
    with client.session_transaction() as session:
        valid_form["csrf_token"] = session["csrf_token"]
    second = client.post("/conoceme/inscripcion", data=valid_form)
    assert first.location == second.location
    assert len(repository.by_email) == 1


def test_operational_and_marketing_consent_are_separate(client, repository, valid_form):
    response = client.post("/conoceme/inscripcion", data=valid_form)
    assert response.status_code == 302
    reference = repository.by_email["ana@example.com"]
    assert repository.by_reference[reference]["marketing_consent"] is False

    valid_form["email"] = "otra@example.com"
    valid_form["marketing_consent"] = "yes"
    client.get("/conoceme")
    with client.session_transaction() as session:
        valid_form["csrf_token"] = session["csrf_token"]
    client.post("/conoceme/inscripcion", data=valid_form)
    reference = repository.by_email["otra@example.com"]
    assert repository.by_reference[reference]["marketing_consent"] is True


def test_operational_consent_is_required(client, valid_form):
    valid_form.pop("operational_consent")
    response = client.post("/conoceme/inscripcion", data=valid_form)
    assert response.status_code == 422
    assert "gestionar la inscripción" in response.get_data(as_text=True)
