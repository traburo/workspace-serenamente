from dataclasses import dataclass

from ..services.states import can_transition


@dataclass(frozen=True)
class RegistrationResult:
    public_reference: str
    created: bool


class PostgresRegistrationRepository:
    def __init__(self, database_url):
        self.database_url = database_url

    def _connect(self):
        if not self.database_url:
            raise RuntimeError("DATABASE_URL no está configurada")
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(self.database_url, row_factory=dict_row)

    def register(self, event_slug, data, allow_draft=False):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id FROM events WHERE slug = %s
                    AND ((status = 'published' AND validation_status = 'validated')
                         OR (%s::boolean AND status = 'draft'))
                    """,
                    (event_slug, allow_draft),
                )
                event = cursor.fetchone()
                if not event:
                    raise LookupError("El evento no está disponible")

                cursor.execute(
                    """
                    INSERT INTO people (full_name, email, whatsapp)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                        full_name = EXCLUDED.full_name,
                        whatsapp = EXCLUDED.whatsapp,
                        updated_at = now()
                    RETURNING id
                    """,
                    (data["adult_name"], data["email"], data["phone"]),
                )
                person_id = cursor.fetchone()["id"]
                cursor.execute(
                    """
                    INSERT INTO registrations (
                        event_id, person_id, status, teen_first_name, teen_age,
                        source, utm_source, utm_medium, utm_campaign,
                        operational_consent, operational_consent_at,
                        marketing_consent, marketing_consent_at
                    ) VALUES (
                        %s, %s, 'pending_payment', %s, %s, %s, %s, %s, %s,
                        TRUE, now(), %s, CASE WHEN %s THEN now() ELSE NULL END
                    )
                    ON CONFLICT (event_id, person_id) DO NOTHING
                    RETURNING public_reference
                    """,
                    (
                        event["id"], person_id, data["teen_first_name"], data["teen_age"],
                        data["source"], data["utm_source"], data["utm_medium"],
                        data["utm_campaign"], data["marketing_consent"],
                        data["marketing_consent"],
                    ),
                )
                created_row = cursor.fetchone()
                created = created_row is not None
                if created:
                    reference = created_row["public_reference"]
                    cursor.execute(
                        """
                        INSERT INTO email_messages (
                            registration_id, event_id, type, recipient_email,
                            scheduled_for, status
                        )
                        SELECT id, event_id, 'registration_received', %s, now(), 'queued'
                        FROM registrations WHERE public_reference = %s
                        ON CONFLICT (registration_id, event_id, type) DO NOTHING
                        """,
                        (data["email"], reference),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT public_reference FROM registrations
                        WHERE event_id = %s AND person_id = %s
                        """,
                        (event["id"], person_id),
                    )
                    reference = cursor.fetchone()["public_reference"]
                return RegistrationResult(reference, created)

    def healthcheck(self):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS ok")
                return cursor.fetchone()["ok"] == 1

    def get_public(self, public_reference):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.public_reference, r.status, e.name AS event_name,
                           e.starts_at, e.timezone, e.location_name, e.location_details
                    FROM registrations r
                    JOIN events e ON e.id = r.event_id
                    WHERE r.public_reference = %s
                    """,
                    (public_reference,),
                )
                return cursor.fetchone()

    def list_registrations(self, status=None):
        query = """
            SELECT r.public_reference, r.status, r.teen_first_name, r.teen_age,
                   r.source, r.created_at, p.full_name AS adult_name,
                   p.email, p.whatsapp
            FROM registrations r
            JOIN people p ON p.id = r.person_id
            JOIN events e ON e.id = r.event_id
            WHERE e.slug = %s
        """
        params = ["conoceme-2026-10-01"]
        if status:
            query += " AND r.status = %s"
            params.append(status)
        query += " ORDER BY r.created_at DESC"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def registration_summary(self):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT e.capacity,
                           count(r.id) AS total,
                           count(*) FILTER (WHERE r.status = 'pending_payment') AS pending_payment,
                           count(*) FILTER (WHERE r.status = 'confirmed') AS confirmed,
                           count(*) FILTER (WHERE r.status = 'attended') AS attended
                    FROM events e
                    LEFT JOIN registrations r ON r.event_id = e.id
                    WHERE e.slug = %s
                    GROUP BY e.capacity
                    """,
                    ("conoceme-2026-10-01",),
                )
                return cursor.fetchone() or {
                    "capacity": 20, "total": 0, "pending_payment": 0,
                    "confirmed": 0, "attended": 0,
                }

    def get_admin(self, public_reference):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.*, p.full_name AS adult_name, p.email, p.whatsapp,
                           e.name AS event_name, e.starts_at, e.location_name,
                           e.location_details, e.price_amount, e.currency,
                           e.payment_deadline, e.capacity
                    FROM registrations r
                    JOIN people p ON p.id = r.person_id
                    JOIN events e ON e.id = r.event_id
                    WHERE r.public_reference = %s
                    """,
                    (public_reference,),
                )
                return cursor.fetchone()

    def transition_status(self, public_reference, new_status, actor, note=None):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, event_id, status FROM registrations WHERE public_reference = %s FOR UPDATE",
                    (public_reference,),
                )
                registration = cursor.fetchone()
                if not registration:
                    raise ValueError("La inscripción no existe.")
                old_status = registration["status"]
                if not can_transition(old_status, new_status):
                    raise ValueError(f"No se puede cambiar de {old_status} a {new_status}.")

                if new_status == "confirmed":
                    cursor.execute(
                        "SELECT capacity FROM events WHERE id = %s FOR UPDATE",
                        (registration["event_id"],),
                    )
                    capacity = cursor.fetchone()["capacity"]
                    cursor.execute(
                        """
                        SELECT count(*) AS occupied FROM registrations
                        WHERE event_id = %s AND status IN ('confirmed','attended','no_show','follow_up_sent')
                        """,
                        (registration["event_id"],),
                    )
                    occupied = cursor.fetchone()["occupied"]
                    if capacity is not None and occupied >= capacity:
                        raise ValueError("No quedan cupos disponibles para confirmar.")

                timestamp_column = {
                    "confirmed": "confirmed_at", "cancelled": "cancelled_at",
                    "attended": "attendance_at",
                }.get(new_status)
                if timestamp_column:
                    cursor.execute(
                        f"UPDATE registrations SET status = %s, {timestamp_column} = now(), "
                        "internal_notes = COALESCE(%s, internal_notes), updated_at = now() WHERE id = %s",
                        (new_status, note, registration["id"]),
                    )
                else:
                    cursor.execute(
                        "UPDATE registrations SET status = %s, internal_notes = COALESCE(%s, internal_notes), "
                        "updated_at = now() WHERE id = %s",
                        (new_status, note, registration["id"]),
                    )

                cursor.execute(
                    """
                    INSERT INTO admin_audit_log (
                        actor_id, action, entity_type, entity_id, before_state, after_state, note
                    ) VALUES (%s, 'status_transition', 'registration', %s,
                              jsonb_build_object('status', %s::text),
                              jsonb_build_object('status', %s::text), %s)
                    """,
                    (actor, registration["id"], old_status, new_status, note),
                )
                if new_status == "confirmed":
                    cursor.execute(
                        """
                        INSERT INTO email_messages (
                            registration_id, event_id, type, recipient_email,
                            scheduled_for, status
                        )
                        SELECT r.id, r.event_id, 'registration_confirmed', p.email, now(), 'queued'
                        FROM registrations r JOIN people p ON p.id = r.person_id
                        WHERE r.id = %s
                        ON CONFLICT (registration_id, event_id, type) DO NOTHING
                        """,
                        (registration["id"],),
                    )

    def list_messages(self, public_reference):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT m.type, m.status, m.scheduled_for, m.sent_at,
                           m.attempt_count, m.last_error
                    FROM email_messages m
                    JOIN registrations r ON r.id = m.registration_id
                    WHERE r.public_reference = %s ORDER BY m.created_at DESC
                    """,
                    (public_reference,),
                )
                return cursor.fetchall()

    def list_audit_log(self, public_reference):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.actor_id, a.action, a.before_state, a.after_state,
                           a.note, a.created_at
                    FROM admin_audit_log a
                    JOIN registrations r ON r.id = a.entity_id
                    WHERE a.entity_type = 'registration' AND r.public_reference = %s
                    ORDER BY a.created_at DESC
                    """,
                    (public_reference,),
                )
                return cursor.fetchall()

    def export_registrations(self, status=None):
        return self.list_registrations(status)

    def enqueue_due_messages(self, include_no_show=False, include_draft=False):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO email_messages (
                        registration_id, event_id, type, recipient_email,
                        scheduled_for, status
                    )
                    SELECT r.id, r.event_id, reminder.type, p.email,
                           e.starts_at - reminder.advance, 'queued'
                    FROM registrations r
                    JOIN events e ON e.id = r.event_id
                    JOIN people p ON p.id = r.person_id
                    CROSS JOIN (VALUES
                        ('reminder_24h'::text, interval '24 hours'),
                        ('reminder_2h'::text, interval '2 hours')
                    ) AS reminder(type, advance)
                    WHERE r.status = 'confirmed'
                      AND (e.status = 'published' OR (%s::boolean AND e.status = 'draft'))
                    ON CONFLICT (registration_id, event_id, type) DO NOTHING
                    """,
                    (include_draft,),
                )
                queued = cursor.rowcount
                cursor.execute(
                    """
                    INSERT INTO email_messages (
                        registration_id, event_id, type, recipient_email,
                        scheduled_for, status
                    )
                    SELECT r.id, r.event_id, followup.type, p.email,
                           e.ends_at + followup.delay, 'queued'
                    FROM registrations r
                    JOIN events e ON e.id = r.event_id
                    JOIN people p ON p.id = r.person_id
                    CROSS JOIN (VALUES
                        ('post_event_thanks'::text, interval '1 hour'),
                        ('follow_up_attendee'::text, interval '48 hours')
                    ) AS followup(type, delay)
                    WHERE r.status = 'attended'
                      AND (e.status IN ('published','completed') OR (%s::boolean AND e.status = 'draft'))
                    ON CONFLICT (registration_id, event_id, type) DO NOTHING
                    """,
                    (include_draft,),
                )
                queued += cursor.rowcount
                if include_no_show:
                    cursor.execute(
                        """
                        INSERT INTO email_messages (
                            registration_id, event_id, type, recipient_email,
                            scheduled_for, status
                        )
                        SELECT r.id, r.event_id, 'post_event_no_show', p.email,
                               e.ends_at + interval '1 hour', 'queued'
                        FROM registrations r
                        JOIN events e ON e.id = r.event_id
                        JOIN people p ON p.id = r.person_id
                        WHERE r.status = 'no_show'
                          AND (e.status IN ('published','completed') OR (%s::boolean AND e.status = 'draft'))
                        ON CONFLICT (registration_id, event_id, type) DO NOTHING
                        """,
                        (include_draft,),
                    )
                    queued += cursor.rowcount
                return queued

    def claim_due_messages(self, limit=25):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    WITH candidates AS (
                        SELECT id FROM email_messages
                        WHERE scheduled_for <= now()
                          AND (status = 'queued' OR
                               (status = 'failed' AND attempt_count < 3 AND updated_at < now() - interval '15 minutes'))
                        ORDER BY scheduled_for
                        FOR UPDATE SKIP LOCKED LIMIT %s
                    )
                    UPDATE email_messages m
                    SET status = 'sending', attempt_count = attempt_count + 1,
                        updated_at = now(), last_error = NULL
                    FROM candidates c, registrations r, people p, events e
                    WHERE m.id = c.id AND r.id = m.registration_id
                      AND p.id = r.person_id AND e.id = m.event_id
                    RETURNING m.id, m.type, m.recipient_email, m.registration_id,
                              m.event_id, r.public_reference, p.full_name AS adult_name,
                              e.name AS event_name, e.starts_at, e.location_name,
                              e.location_details
                    """,
                    (limit,),
                )
                return cursor.fetchall()

    def mark_message_sent(self, message_id, provider_message_id):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT registration_id, type FROM email_messages WHERE id = %s FOR UPDATE",
                    (message_id,),
                )
                message = cursor.fetchone()
                cursor.execute(
                    """
                    UPDATE email_messages SET status = 'sent', provider_message_id = %s,
                        sent_at = now(), updated_at = now() WHERE id = %s AND status = 'sending'
                    """,
                    (provider_message_id, message_id),
                )
                if message and message["type"] in ("follow_up_attendee", "post_event_no_show"):
                    cursor.execute(
                        "SELECT status FROM registrations WHERE id = %s FOR UPDATE",
                        (message["registration_id"],),
                    )
                    registration = cursor.fetchone()
                    if registration and registration["status"] in ("attended", "no_show"):
                        old_status = registration["status"]
                        cursor.execute(
                            "UPDATE registrations SET status = 'follow_up_sent', updated_at = now() WHERE id = %s",
                            (message["registration_id"],),
                        )
                        cursor.execute(
                            """
                            INSERT INTO admin_audit_log (
                                actor_id, action, entity_type, entity_id,
                                before_state, after_state, note
                            ) VALUES (
                                'system:message-job', 'status_transition', 'registration', %s,
                                jsonb_build_object('status', %s::text),
                                jsonb_build_object('status', 'follow_up_sent'),
                                'Seguimiento postexperiencia enviado'
                            )
                            """,
                            (message["registration_id"], old_status),
                        )

    def mark_message_failed(self, message_id, error):
        safe_error = f"{type(error).__name__}: {str(error)[:180]}"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE email_messages SET status = 'failed', last_error = %s,
                        updated_at = now() WHERE id = %s AND status = 'sending'
                    """,
                    (safe_error, message_id),
                )
