CONTENT_STATUS_LABELS = {
    "draft": "Borrador",
    "in_control": "En control",
    "for_review": "Para revisión",
    "changes_requested": "Cambios solicitados",
    "approved": "Aprobada",
    "published": "Publicada",
    "measured": "Medida",
}

CONTENT_TRANSITIONS = {
    "draft": {"in_control"},
    "in_control": {"for_review", "changes_requested"},
    "for_review": {"approved", "changes_requested"},
    "changes_requested": {"in_control"},
    "approved": {"published"},
    "published": {"measured"},
    "measured": set(),
}


def can_transition_content(current_status, new_status):
    return new_status in CONTENT_TRANSITIONS.get(current_status, set())
