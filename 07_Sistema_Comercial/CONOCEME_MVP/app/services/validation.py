import re


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
NAME_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]{2,80}$")


def _clean(value, maximum=120):
    return " ".join((value or "").strip().split())[:maximum]


def _phone(value):
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("56") and len(digits) == 11:
        return f"+{digits}"
    if len(digits) == 9:
        return f"+56{digits}"
    return ""


def validate_registration(values):
    errors = {}
    adult_name = _clean(values.get("adult_name"), 100)
    email = _clean(values.get("email"), 254).lower()
    phone = _phone(values.get("phone"))
    teen_first_name = _clean(values.get("teen_first_name"), 60)

    if not NAME_RE.fullmatch(adult_name):
        errors["adult_name"] = "Ingresa el nombre del adulto responsable."
    if not EMAIL_RE.fullmatch(email):
        errors["email"] = "Ingresa un correo válido."
    if not phone:
        errors["phone"] = "Ingresa un teléfono chileno válido de 9 dígitos."
    if not NAME_RE.fullmatch(teen_first_name):
        errors["teen_first_name"] = "Ingresa solo el nombre de pila del adolescente."

    try:
        teen_age = int(values.get("teen_age", ""))
        if teen_age < 12 or teen_age > 17:
            raise ValueError
    except (TypeError, ValueError):
        teen_age = None
        errors["teen_age"] = "La experiencia está dirigida a adolescentes de 12 a 17 años."

    operational_consent = values.get("operational_consent") == "yes"
    marketing_consent = values.get("marketing_consent") == "yes"
    if not operational_consent:
        errors["operational_consent"] = "Necesitamos esta autorización para gestionar la inscripción."

    source = _clean(values.get("source"), 40).lower() or "direct"
    allowed_sources = {"instagram", "whatsapp", "referral", "qr", "direct", "other"}
    if source not in allowed_sources:
        source = "other"

    return errors, {
        "adult_name": adult_name,
        "email": email,
        "phone": phone,
        "teen_first_name": teen_first_name,
        "teen_age": teen_age,
        "operational_consent": operational_consent,
        "marketing_consent": marketing_consent,
        "source": source,
        "utm_source": _clean(values.get("utm_source"), 100) or None,
        "utm_medium": _clean(values.get("utm_medium"), 100) or None,
        "utm_campaign": _clean(values.get("utm_campaign"), 100) or None,
    }
