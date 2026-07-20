ALLOWED_TRANSITIONS = {
    "received": {"pending_payment", "cancelled"},
    "pending_payment": {"confirmed", "cancelled"},
    "confirmed": {"attended", "no_show", "cancelled"},
    "attended": {"follow_up_sent"},
    "no_show": {"follow_up_sent"},
    "cancelled": set(),
    "follow_up_sent": set(),
}


STATUS_LABELS = {
    "received": "Recibida",
    "pending_payment": "Pago pendiente",
    "confirmed": "Confirmada",
    "cancelled": "Cancelada",
    "attended": "Asistió",
    "no_show": "No asistió",
    "follow_up_sent": "Seguimiento enviado",
}


def can_transition(current_status, new_status):
    return new_status in ALLOWED_TRANSITIONS.get(current_status, set())
