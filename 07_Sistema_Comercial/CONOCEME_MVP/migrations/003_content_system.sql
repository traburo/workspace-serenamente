CREATE TABLE content_campaigns (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    objective text NOT NULL,
    audience text NOT NULL,
    theme text NOT NULL,
    starts_on date NOT NULL,
    ends_on date NOT NULL CHECK (ends_on >= starts_on),
    status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','active','completed','archived')),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE content_pieces (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES content_campaigns(id) ON DELETE CASCADE,
    title text NOT NULL,
    pillar text NOT NULL CHECK (pillar IN ('Comprender','Respirar','Avanzar','Conectar')),
    format text NOT NULL CHECK (format IN ('Carrusel','Reel','Publicación','Historias')),
    status text NOT NULL DEFAULT 'draft' CHECK (status IN
        ('draft','in_control','for_review','changes_requested','approved','published','measured')),
    scheduled_for timestamptz,
    objective text,
    cta text,
    caption text,
    script text,
    visual_direction text,
    sources text,
    assumptions text,
    approval_pending text,
    blocking_issues text[] NOT NULL DEFAULT '{}',
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX content_pieces_campaign_idx ON content_pieces(campaign_id, scheduled_for);

CREATE TABLE content_reviews (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    piece_id uuid NOT NULL REFERENCES content_pieces(id) ON DELETE CASCADE,
    reviewer text NOT NULL,
    decision text NOT NULL,
    comment text,
    previous_status text NOT NULL,
    new_status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX content_reviews_piece_idx ON content_reviews(piece_id, created_at DESC);

CREATE TABLE content_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    piece_id uuid NOT NULL REFERENCES content_pieces(id) ON DELETE CASCADE,
    followers_gained integer NOT NULL DEFAULT 0 CHECK (followers_gained >= 0),
    reach integer NOT NULL DEFAULT 0 CHECK (reach >= 0),
    saves integer NOT NULL DEFAULT 0 CHECK (saves >= 0),
    shares integer NOT NULL DEFAULT 0 CHECK (shares >= 0),
    comments integer NOT NULL DEFAULT 0 CHECK (comments >= 0),
    replies integer NOT NULL DEFAULT 0 CHECK (replies >= 0),
    learning text,
    recorded_at timestamptz NOT NULL DEFAULT now()
);
