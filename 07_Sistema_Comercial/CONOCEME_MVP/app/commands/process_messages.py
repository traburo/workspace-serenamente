import json
import os

from app.repositories.registrations import PostgresRegistrationRepository
from app.services.email import ResendEmailService
from app.services.message_jobs import MessageProcessor


def main():
    repository = PostgresRegistrationRepository(os.environ.get("DATABASE_URL", ""))
    email_service = ResendEmailService(
        os.environ.get("RESEND_API_KEY", ""),
        os.environ.get("RESEND_FROM_EMAIL", ""),
        simulate=os.environ.get("EMAIL_SIMULATION", "0") == "1",
    )
    result = MessageProcessor(
        repository, email_service,
        include_no_show=os.environ.get("ENABLE_NO_SHOW_FOLLOWUP", "0") == "1",
        include_draft=os.environ.get("STAGING_MODE", "0") == "1",
        recipient_override=os.environ.get("STAGING_EMAIL_OVERRIDE") or None,
    ).run()
    print(json.dumps(result, ensure_ascii=False))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
