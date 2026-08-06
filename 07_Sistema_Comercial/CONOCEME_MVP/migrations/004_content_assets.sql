CREATE TABLE content_assets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    piece_id uuid NOT NULL REFERENCES content_pieces(id) ON DELETE CASCADE,
    kind text NOT NULL CHECK (kind IN ('image')),
    provider text NOT NULL,
    model text NOT NULL,
    prompt text NOT NULL,
    mime_type text NOT NULL CHECK (mime_type IN ('image/png','image/jpeg','image/webp')),
    content bytea NOT NULL CHECK (octet_length(content) > 0 AND octet_length(content) <= 12582912),
    status text NOT NULL DEFAULT 'pending_review' CHECK (status IN ('pending_review','approved','rejected')),
    created_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    reviewer text,
    reviewed_at timestamptz,
    CHECK ((status = 'pending_review' AND reviewer IS NULL AND reviewed_at IS NULL)
        OR (status IN ('approved','rejected') AND reviewer IS NOT NULL AND reviewed_at IS NOT NULL))
);

CREATE INDEX content_assets_piece_idx ON content_assets(piece_id, created_at DESC);
