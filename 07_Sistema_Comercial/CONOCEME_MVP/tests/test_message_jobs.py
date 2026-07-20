from app.services.email import ResendEmailService
from app.services.message_jobs import MessageProcessor
from app.services.message_jobs import render_message


class MessageRepository:
    def __init__(self):
        self.enqueued = False
        self.claimed = False
        self.sent = []
        self.failed = []

    def enqueue_due_messages(self, _include_no_show=False, _include_draft=False):
        if self.enqueued:
            return 0
        self.enqueued = True
        return 2

    def claim_due_messages(self, _limit):
        if self.claimed:
            return []
        self.claimed = True
        return [{
            "id": "message-1", "type": "reminder_24h",
            "recipient_email": "ana@example.com", "registration_id": "registration-1",
            "event_id": "event-1", "public_reference": "CN-TEST0001",
            "adult_name": "Ana Pérez", "event_name": "CONÓCEME",
            "location_name": "Sede Pedro Fontova", "location_details": None,
        }]

    def mark_message_sent(self, message_id, provider_id):
        self.sent.append((message_id, provider_id))

    def mark_message_failed(self, message_id, error):
        self.failed.append((message_id, error))


def test_message_job_is_idempotent():
    repository = MessageRepository()
    processor = MessageProcessor(
        repository, ResendEmailService("", "", simulate=True)
    )
    first = processor.run()
    second = processor.run()
    assert first == {"queued": 2, "claimed": 1, "sent": 1, "failed": 0}
    assert second == {"queued": 0, "claimed": 0, "sent": 0, "failed": 0}
    assert len(repository.sent) == 1


def test_post_event_messages_are_warm_and_non_clinical():
    base = {
        "adult_name": "Ana Pérez", "event_name": "CONÓCEME",
        "location_name": "Sede Pedro Fontova", "location_details": None,
        "public_reference": "CN-TEST0001",
    }
    for message_type in ("post_event_thanks", "follow_up_attendee", "post_event_no_show"):
        subject, html = render_message({**base, "type": message_type})
        combined = (subject + html).lower()
        assert "conóceme" in combined
        assert "diagnóstico" not in combined
        assert "garantizado" not in combined


def test_staging_recipient_override_prevents_external_delivery():
    repository = MessageRepository()

    class CapturingEmailService:
        def __init__(self):
            self.recipients = []

        def send(self, **message):
            self.recipients.append(message["to"])
            return {"id": "simulated"}

    service = CapturingEmailService()
    processor = MessageProcessor(
        repository, service, include_draft=True,
        recipient_override="awmc18@gmail.com",
    )
    processor.run()
    assert service.recipients == ["awmc18@gmail.com"]
