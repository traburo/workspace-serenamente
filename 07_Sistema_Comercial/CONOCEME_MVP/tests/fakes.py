from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.services.content_states import can_transition_content
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


class MemoryContentRepository:
    def __init__(self):
        self.campaigns = {}
        self.pieces = {}
        self.reviews = []
        self.assets = {}

    def list_campaigns(self):
        rows = []
        for campaign in self.campaigns.values():
            pieces = [p for p in self.pieces.values() if p["campaign_id"] == campaign["id"]]
            rows.append({**campaign, "piece_count": len(pieces),
                         "approved_count": sum(p["status"] == "approved" for p in pieces)})
        return rows

    def create_campaign(self, data, actor):
        campaign_id = uuid4()
        self.campaigns[campaign_id] = {
            "id": campaign_id, **data, "created_by": actor, "status": "draft",
            "starts_on": datetime.fromisoformat(data["starts_on"]).date(),
            "ends_on": datetime.fromisoformat(data["ends_on"]).date(),
            "created_at": datetime.now(timezone.utc),
        }
        return campaign_id

    def get_campaign(self, campaign_id):
        return self.campaigns.get(campaign_id)

    def list_pieces(self, campaign_id):
        return [p for p in self.pieces.values() if p["campaign_id"] == campaign_id]

    def create_piece(self, campaign_id, data, actor):
        piece_id = uuid4()
        self.pieces[piece_id] = {
            "id": piece_id, "campaign_id": campaign_id, **data, "status": "draft",
            "created_by": actor, "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        return piece_id

    def create_generated_pieces(self, campaign_id, pieces, actor):
        if self.list_pieces(campaign_id):
            raise ValueError("La campaña ya contiene piezas. La generación automática solo se ejecuta una vez.")
        for piece in pieces:
            self.create_piece(campaign_id, piece, actor)

    def get_piece(self, piece_id):
        piece = self.pieces.get(piece_id)
        if not piece:
            return None
        return {**piece, "campaign_title": self.campaigns[piece["campaign_id"]]["title"]}

    def update_piece(self, piece_id, data):
        if self.pieces[piece_id]["status"] not in {"draft", "in_control", "changes_requested"}:
            raise ValueError("La pieza debe volver a cambios antes de editarse.")
        self.pieces[piece_id].update(data)

    def transition_piece(self, piece_id, new_status, actor, comment=None):
        piece = self.pieces.get(piece_id)
        if not piece or not can_transition_content(piece["status"], new_status):
            raise ValueError("Ese cambio de estado no está permitido.")
        if new_status == "approved" and piece["blocking_issues"]:
            raise ValueError("Resuelve los bloqueos antes de aprobar la pieza.")
        if new_status == "approved" and any(
            asset["piece_id"] == piece_id and asset["status"] == "pending_review"
            for asset in self.assets.values()
        ):
            raise ValueError("Revisa las imágenes generadas antes de aprobar la pieza.")
        previous = piece["status"]
        piece["status"] = new_status
        self.reviews.append({
            "piece_id": piece_id, "reviewer": actor, "decision": new_status,
            "comment": comment, "previous_status": previous, "new_status": new_status,
            "created_at": datetime.now(timezone.utc),
        })

    def list_reviews(self, piece_id):
        return [r for r in reversed(self.reviews) if r["piece_id"] == piece_id]

    def save_image_asset(self, piece_id, prompt, generated, actor):
        asset_id = uuid4()
        self.assets[asset_id] = {
            "id": asset_id, "piece_id": piece_id, "prompt": prompt,
            "provider": "google-gemini", "model": generated.model,
            "mime_type": generated.mime_type, "content": generated.data,
            "created_by": actor, "created_at": datetime.now(timezone.utc),
            "status": "pending_review", "reviewer": None, "reviewed_at": None,
        }
        return asset_id

    def list_image_assets(self, piece_id):
        return [a for a in self.assets.values() if a["piece_id"] == piece_id]

    def get_image_asset(self, asset_id):
        return self.assets.get(asset_id)

    def review_image_asset(self, asset_id, status, reviewer):
        if status not in {"approved", "rejected"}:
            raise ValueError("La decisión sobre la imagen no es válida.")
        asset = self.assets.get(asset_id)
        if not asset or asset["status"] != "pending_review":
            raise ValueError("La imagen no existe o ya fue revisada.")
        asset.update({"status": status, "reviewer": reviewer,
                      "reviewed_at": datetime.now(timezone.utc)})
        return asset["piece_id"]
