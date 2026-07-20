import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from tests.fakes import MemoryRegistrationRepository


@pytest.fixture
def repository():
    return MemoryRegistrationRepository()


@pytest.fixture
def app(repository):
    return create_app(
        {
            "TESTING": True, "SECRET_KEY": "test-secret",
            "CONTACT_WHATSAPP": "56937033936", "ADMIN_USERNAME": "alex",
            "ADMIN_PASSWORD_HASH": generate_password_hash("test-password"),
        },
        repository=repository,
    )


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_form(client):
    client.get("/conoceme")
    with client.session_transaction() as session:
        token = session["csrf_token"]
    return {
        "csrf_token": token,
        "adult_name": "Ana Pérez",
        "email": "ana@example.com",
        "phone": "9 1234 5678",
        "teen_first_name": "Sofía",
        "teen_age": "15",
        "source": "instagram",
        "operational_consent": "yes",
    }
