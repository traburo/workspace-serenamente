from dataclasses import dataclass
from datetime import datetime, timezone

from app.services.states import can_transition


@dataclass
class Result:
    public_reference: str
    created: bool


class MemoryRegistrationRepository:
    def __init__(self):
        self.by_email = {}
        self.by_reference = {}
        self.audit = []
        self.messages = []

    def register(self, event_slug, data, allow_draft=False):
        if data["email"] in self.by_email:
            return Result(self.by_email[data["email"]], False)
        reference = f"CN-TEST{len(self.by_email) + 1:04d}"
        self.by_email[data["email"]] = reference
        self.by_reference[reference] = {
            "public_reference": reference,
            "status": "pending_payment",
            "event_name": "CONÓCEME",
            "marketing_consent": data["marketing_consent"],
            "adult_name": data["adult_name"], "email": data["email"],
            "whatsapp": data["phone"], "teen_first_name": data["teen_first_name"],
            "teen_age": data["teen_age"], "source": data["source"],
            "created_at": datetime.now(timezone.utc),
        }
        return Result(reference, True)

    def get_public(self, public_reference):
        return self.by_reference.get(public_reference)

    def healthcheck(self):
        return True

    def list_registrations(self, status=None):
        rows = list(self.by_reference.values())
        return [row for row in rows if not status or row["status"] == status]

    def registration_summary(self):
        rows = list(self.by_reference.values())
        return {
            "capacity": 20, "total": len(rows),
            "pending_payment": sum(row["status"] == "pending_payment" for row in rows),
            "confirmed": sum(row["status"] == "confirmed" for row in rows),
            "attended": sum(row["status"] == "attended" for row in rows),
        }

    def get_admin(self, public_reference):
        return self.by_reference.get(public_reference)

    def transition_status(self, public_reference, new_status, actor, note=None):
        row = self.by_reference.get(public_reference)
        if not row or not can_transition(row["status"], new_status):
            raise ValueError("Transición no permitida")
        if new_status == "confirmed":
            confirmed = sum(item["status"] == "confirmed" for item in self.by_reference.values())
            if confirmed >= 20:
                raise ValueError("No quedan cupos disponibles para confirmar.")
        old_status = row["status"]
        row["status"] = new_status
        self.audit.append({"public_reference": public_reference, "actor_id": actor,
                           "before_state": {"status": old_status},
                           "after_state": {"status": new_status}, "note": note,
                           "action": "status_transition", "created_at": datetime.now(timezone.utc)})

    def list_messages(self, public_reference):
        return [item for item in self.messages if item.get("public_reference") == public_reference]

    def list_audit_log(self, public_reference):
        return [item for item in self.audit if item["public_reference"] == public_reference]

    def export_registrations(self, status=None):
        return self.list_registrations(status)
