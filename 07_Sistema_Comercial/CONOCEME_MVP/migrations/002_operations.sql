ALTER TABLE events
    ADD COLUMN capacity integer CHECK (capacity > 0),
    ADD COLUMN payment_deadline timestamptz,
    ADD COLUMN payment_receipt_email text,
    ADD COLUMN refund_policy text;

CREATE TABLE admin_audit_log (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id text NOT NULL,
    action text NOT NULL,
    entity_type text NOT NULL,
    entity_id uuid NOT NULL,
    before_state jsonb,
    after_state jsonb,
    note text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX admin_audit_log_entity_idx
    ON admin_audit_log (entity_type, entity_id, created_at DESC);

UPDATE events SET
    starts_at = '2026-10-01 12:00:00 America/Santiago',
    ends_at = '2026-10-01 15:00:00 America/Santiago',
    location_name = 'Sede Pedro Fontova',
    location_details = NULL,
    price_amount = 30000,
    capacity = 20,
    payment_deadline = '2026-09-30 23:59:59 America/Santiago',
    payment_receipt_email = 'awmc18@gmail.com',
    refund_policy = 'Provisional: 100% hasta 7 días antes; entre 6 días y 48 horas, 50% o abono completo; dentro de 48 horas o inasistencia, sin devolución y con transferencia de cupo permitida. Derechos legales prevalecen.',
    updated_at = now()
WHERE slug = 'conoceme-2026-10-01';

-- El evento sigue como borrador. Solo una aprobación humana autoriza este cambio:
-- UPDATE events SET status='published', validation_status='validated'
-- WHERE slug='conoceme-2026-10-01';
