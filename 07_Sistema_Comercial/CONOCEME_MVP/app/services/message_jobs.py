from html import escape


SUBJECTS = {
    "registration_received": "Recibimos tu inscripción a CONÓCEME",
    "registration_confirmed": "Tu cupo para CONÓCEME está confirmado",
    "reminder_24h": "CONÓCEME es mañana",
    "reminder_2h": "CONÓCEME comienza en 2 horas",
    "post_event_thanks": "Gracias por participar en CONÓCEME",
    "follow_up_attendee": "Una invitación para continuar en casa",
    "post_event_no_show": "Sobre tu inscripción a CONÓCEME",
}


def render_message(message):
    adult_name = escape(message["adult_name"])
    event_name = escape(message["event_name"])
    location = escape(
        " · ".join(filter(None, [message.get("location_name"), message.get("location_details")]))
    )
    reference = escape(message["public_reference"])
    message_type = message["type"]
    if message_type == "registration_received":
        body = (
            f"<p>Hola {adult_name}, recibimos tu inscripción a <strong>{event_name}</strong>.</p>"
            "<p>El cupo queda pendiente hasta que Alex Martínez verifique el pago.</p>"
        )
    elif message_type == "registration_confirmed":
        body = (
            f"<p>Hola {adult_name}, tu cupo para <strong>{event_name}</strong> está confirmado.</p>"
            f"<p>Lugar: {location}.</p>"
        )
    elif message_type == "reminder_24h":
        body = (
            f"<p>Hola {adult_name}, te recordamos que <strong>{event_name}</strong> es mañana.</p>"
            f"<p>Horario: 12:00 a 15:00. Lugar: {location}.</p>"
        )
    elif message_type == "reminder_2h":
        body = (
            f"<p>Hola {adult_name}, <strong>{event_name}</strong> comienza en 2 horas.</p>"
            f"<p>Te esperamos en {location}.</p>"
        )
    elif message_type == "post_event_thanks":
        body = (
            f"<p>Hola {adult_name}, gracias por participar en <strong>{event_name}</strong>.</p>"
            "<p>Esperamos que este encuentro les haya ofrecido un momento para escucharse y conocerse desde una nueva perspectiva.</p>"
            "<p>Pueden volver a los recursos entregados cuando lo consideren oportuno. No es necesario responder este correo ni compartir información personal.</p>"
        )
    elif message_type == "follow_up_attendee":
        body = (
            f"<p>Hola {adult_name}, han pasado unos días desde <strong>{event_name}</strong>.</p>"
            "<p>Si les hace sentido, pueden elegir un momento breve para retomar el compromiso que construyeron y escucharse sin presión. Cada integrante de la dupla puede decidir cuánto desea compartir.</p>"
            "<p>Los recursos entregados durante la experiencia quedan disponibles para acompañar esa continuidad en casa.</p>"
        )
    elif message_type == "post_event_no_show":
        body = (
            f"<p>Hola {adult_name}, vimos que finalmente no pudieron acompañarnos en <strong>{event_name}</strong>.</p>"
            "<p>Esperamos que estén bien. Si necesitan revisar una situación administrativa relacionada con su inscripción, pueden responder este correo.</p>"
            "<p>Este mensaje no requiere respuesta.</p>"
        )
    else:
        raise ValueError(f"Tipo de mensaje no soportado: {message_type}")
    return SUBJECTS[message_type], body + f"<p>Referencia: {reference}</p>"


class MessageProcessor:
    def __init__(self, repository, email_service, include_no_show=False,
                 include_draft=False, recipient_override=None):
        self.repository = repository
        self.email_service = email_service
        self.include_no_show = include_no_show
        self.include_draft = include_draft
        self.recipient_override = recipient_override

    def run(self, limit=25):
        queued = self.repository.enqueue_due_messages(
            self.include_no_show, self.include_draft
        )
        messages = self.repository.claim_due_messages(limit)
        sent = 0
        failed = 0
        for message in messages:
            try:
                subject, html = render_message(message)
                result = self.email_service.send(
                    to=self.recipient_override or message["recipient_email"],
                    subject=subject, html=html,
                    idempotency_key=(
                        f"{message['registration_id']}:{message['event_id']}:{message['type']}"
                    ),
                )
                self.repository.mark_message_sent(message["id"], result["id"])
                sent += 1
            except Exception as error:
                self.repository.mark_message_failed(message["id"], error)
                failed += 1
        return {"queued": queued, "claimed": len(messages), "sent": sent, "failed": failed}
