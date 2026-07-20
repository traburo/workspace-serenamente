from app.services.email import ResendEmailService


def test_resend_simulation_returns_deterministic_provider_id():
    service = ResendEmailService("", "", simulate=True)
    result = service.send(
        to="ana@example.com", subject="Recibimos tu inscripción",
        html="<p>Gracias</p>", idempotency_key="registration:one:received",
    )
    assert result["id"] == "simulated:registration:one:received"
