import os

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.repositories.registrations import PostgresRegistrationRepository
from app.services.email import ResendEmailService
from app.services.message_jobs import MessageProcessor


DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="TEST_DATABASE_URL no configurada")


def _csrf(client):
    with client.session_transaction() as session:
        return session["csrf_token"]


def test_complete_commercial_journey_with_real_postgres():
    repository = PostgresRegistrationRepository(DATABASE_URL)
    with repository._connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE admin_audit_log, email_messages, registrations, people RESTART IDENTITY CASCADE")
            cursor.execute(
                """
                UPDATE events SET status='published', validation_status='validated',
                    starts_at=now() + interval '1 hour', ends_at=now() + interval '4 hours'
                WHERE slug='conoceme-2026-10-01'
                """
            )

    app = create_app({
        "TESTING": True, "SECRET_KEY": "postgres-test-secret",
        "ADMIN_USERNAME": "alex",
        "ADMIN_PASSWORD_HASH": generate_password_hash("test-password"),
        "DATABASE_URL": DATABASE_URL,
    }, repository=repository)
    client = app.test_client()

    client.get("/conoceme")
    response = client.post("/conoceme/inscripcion", data={
        "csrf_token": _csrf(client), "adult_name": "Prueba Integral",
        "email": "integral@example.com", "phone": "9 1234 5678",
        "teen_first_name": "Sofía", "teen_age": "15", "source": "direct",
        "operational_consent": "yes",
    })
    assert response.status_code == 302
    reference = response.location.rsplit("/", 1)[-1]

    client.get("/admin/login")
    response = client.post("/admin/login", data={
        "csrf_token": _csrf(client), "username": "alex", "password": "test-password",
    })
    assert response.status_code == 302
    response = client.post(f"/admin/registrations/{reference}/status", data={
        "csrf_token": _csrf(client), "status": "confirmed", "note": "Pago de prueba verificado",
    })
    assert response.status_code == 302
    assert client.get("/admin/registrations.csv").status_code == 200

    processor = MessageProcessor(repository, ResendEmailService("", "", simulate=True))
    first_messages = processor.run()
    assert first_messages["sent"] == 4

    response = client.post(f"/admin/registrations/{reference}/status", data={
        "csrf_token": _csrf(client), "status": "attended", "note": "Asistencia de prueba",
    })
    assert response.status_code == 302
    with repository._connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE events SET starts_at=now() - interval '53 hours',
                    ends_at=now() - interval '50 hours'
                WHERE slug='conoceme-2026-10-01'
                """
            )

    post_messages = processor.run()
    repeated_run = processor.run()
    assert post_messages["sent"] == 2
    assert repeated_run["sent"] == 0

    registration = repository.get_admin(reference)
    assert registration["status"] == "follow_up_sent"
    messages = repository.list_messages(reference)
    assert len(messages) == 6
    assert all(message["status"] == "sent" for message in messages)
    assert len(repository.list_audit_log(reference)) == 3
