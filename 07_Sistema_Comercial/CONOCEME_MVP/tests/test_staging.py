from app import create_app
from tests.fakes import MemoryRegistrationRepository


def test_staging_banner_and_draft_registration():
    repository = MemoryRegistrationRepository()
    app = create_app({
        "TESTING": True, "SECRET_KEY": "staging-test", "STAGING_MODE": True,
    }, repository=repository)
    client = app.test_client()
    response = client.get("/conoceme")
    content = response.get_data(as_text=True)
    assert "ENTORNO DE PRUEBA" in content
    assert "no realices transferencias" in content
    with client.session_transaction() as session:
        token = session["csrf_token"]
    response = client.post("/conoceme/inscripcion", data={
        "csrf_token": token, "adult_name": "Persona Prueba",
        "email": "prueba@example.com", "phone": "9 1234 5678",
        "teen_first_name": "Sofía", "teen_age": "15", "source": "direct",
        "operational_consent": "yes",
    })
    assert response.status_code == 302
