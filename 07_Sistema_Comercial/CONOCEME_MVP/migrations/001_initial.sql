CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug text NOT NULL UNIQUE,
    name text NOT NULL,
    status text NOT NULL CHECK (status IN ('draft','published','closed','completed','cancelled')),
    validation_status text NOT NULL CHECK (validation_status IN ('pending_human_validation','validated')),
    starts_at timestamptz NOT NULL,
    ends_at timestamptz NOT NULL,
    timezone text NOT NULL DEFAULT 'America/Santiago',
    location_name text NOT NULL,
    location_details text,
    price_amount integer CHECK (price_amount >= 0),
    currency char(3) NOT NULL DEFAULT 'CLP',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE people (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name text NOT NULL,
    email text NOT NULL UNIQUE,
    whatsapp text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE registrations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    public_reference text NOT NULL UNIQUE DEFAULT ('CN-' || upper(substr(encode(gen_random_bytes(8), 'hex'), 1, 10))),
    event_id uuid NOT NULL REFERENCES events(id),
    person_id uuid NOT NULL REFERENCES people(id),
    status text NOT NULL CHECK (status IN ('received','pending_payment','confirmed','cancelled','attended','no_show','follow_up_sent')),
    teen_first_name text NOT NULL,
    teen_age smallint NOT NULL CHECK (teen_age BETWEEN 12 AND 17),
    source text NOT NULL,
    utm_source text,
    utm_medium text,
    utm_campaign text,
    operational_consent boolean NOT NULL CHECK (operational_consent),
    operational_consent_at timestamptz NOT NULL,
    marketing_consent boolean NOT NULL DEFAULT false,
    marketing_consent_at timestamptz,
    internal_notes text,
    attendance_at timestamptz,
    confirmed_at timestamptz,
    cancelled_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (event_id, person_id)
);

CREATE TABLE email_messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    registration_id uuid NOT NULL REFERENCES registrations(id),
    event_id uuid NOT NULL REFERENCES events(id),
    type text NOT NULL,
    recipient_email text NOT NULL,
    scheduled_for timestamptz NOT NULL,
    status text NOT NULL CHECK (status IN ('queued','sending','sent','failed','cancelled')),
    provider_message_id text,
    attempt_count integer NOT NULL DEFAULT 0,
    last_error text,
    sent_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (registration_id, event_id, type)
);

INSERT INTO events (
    slug, name, status, validation_status, starts_at, ends_at,
    location_name, location_details, price_amount
) VALUES (
    'conoceme-2026-10-01', 'CONÓCEME', 'draft', 'pending_human_validation',
    '2026-10-01 12:00:00 America/Santiago', '2026-10-01 15:00:00 America/Santiago',
    'Sede Pedro Fontova', NULL, 30000
) ON CONFLICT (slug) DO NOTHING;

-- La publicación exige validación humana. Ejecutar solo después de aprobar el evento:
-- UPDATE events SET status='published', validation_status='validated' WHERE slug='conoceme-2026-10-01';
