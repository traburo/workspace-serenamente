from ..services.content_states import can_transition_content


class PostgresContentRepository:
    def __init__(self, database_url):
        self.database_url = database_url

    def _connect(self):
        if not self.database_url:
            raise RuntimeError("DATABASE_URL no está configurada")
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(self.database_url, row_factory=dict_row)

    def list_campaigns(self):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.*, count(p.id) AS piece_count,
                       count(p.id) FILTER (WHERE p.status = 'approved') AS approved_count
                FROM content_campaigns c
                LEFT JOIN content_pieces p ON p.campaign_id = c.id
                GROUP BY c.id ORDER BY c.starts_on DESC, c.created_at DESC
                """
            )
            return cursor.fetchall()

    def create_campaign(self, data, actor):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO content_campaigns
                    (title, objective, audience, theme, starts_on, ends_on, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (data["title"], data["objective"], data["audience"], data["theme"],
                 data["starts_on"], data["ends_on"], actor),
            )
            return cursor.fetchone()["id"]

    def get_campaign(self, campaign_id):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT * FROM content_campaigns WHERE id = %s", (campaign_id,))
            return cursor.fetchone()

    def list_pieces(self, campaign_id):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM content_pieces WHERE campaign_id = %s "
                "ORDER BY scheduled_for NULLS LAST, created_at",
                (campaign_id,),
            )
            return cursor.fetchall()

    def create_piece(self, campaign_id, data, actor):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO content_pieces
                    (campaign_id, title, pillar, format, scheduled_for, objective, cta,
                     caption, script, visual_direction, sources, assumptions,
                     approval_pending, blocking_issues, created_by)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (campaign_id, data["title"], data["pillar"], data["format"],
                 data.get("scheduled_for") or None, data.get("objective"), data.get("cta"),
                 data.get("caption"), data.get("script"), data.get("visual_direction"),
                 data.get("sources"), data.get("assumptions"), data.get("approval_pending"),
                 data.get("blocking_issues", []), actor),
            )
            return cursor.fetchone()["id"]

    def create_generated_pieces(self, campaign_id, pieces, actor):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM content_pieces WHERE campaign_id=%s LIMIT 1", (campaign_id,))
            if cursor.fetchone():
                raise ValueError("La campaña ya contiene piezas. La generación automática solo se ejecuta una vez.")
            for data in pieces:
                cursor.execute(
                    """
                    INSERT INTO content_pieces
                        (campaign_id, title, pillar, format, scheduled_for, objective, cta,
                         caption, script, visual_direction, sources, assumptions,
                         approval_pending, blocking_issues, created_by)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (campaign_id, data["title"], data["pillar"], data["format"],
                     data.get("scheduled_for") or None, data.get("objective"), data.get("cta"),
                     data.get("caption"), data.get("script"), data.get("visual_direction"),
                     data.get("sources"), data.get("assumptions"), data.get("approval_pending"),
                     data.get("blocking_issues", []), actor),
                )

    def get_piece(self, piece_id):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.*, c.title AS campaign_title FROM content_pieces p
                JOIN content_campaigns c ON c.id = p.campaign_id WHERE p.id = %s
                """,
                (piece_id,),
            )
            return cursor.fetchone()

    def update_piece(self, piece_id, data):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT status FROM content_pieces WHERE id=%s FOR UPDATE", (piece_id,))
            piece = cursor.fetchone()
            if not piece:
                raise ValueError("La pieza no existe.")
            if piece["status"] not in {"draft", "in_control", "changes_requested"}:
                raise ValueError("La pieza debe volver a cambios antes de editarse.")
            cursor.execute(
                """
                UPDATE content_pieces SET title=%s, pillar=%s, format=%s,
                    scheduled_for=%s, objective=%s, cta=%s, caption=%s, script=%s,
                    visual_direction=%s, sources=%s, assumptions=%s,
                    approval_pending=%s, blocking_issues=%s, updated_at=now()
                WHERE id=%s
                """,
                (data["title"], data["pillar"], data["format"],
                 data.get("scheduled_for") or None, data.get("objective"), data.get("cta"),
                 data.get("caption"), data.get("script"), data.get("visual_direction"),
                 data.get("sources"), data.get("assumptions"), data.get("approval_pending"),
                 data.get("blocking_issues", []), piece_id),
            )

    def transition_piece(self, piece_id, new_status, actor, comment=None):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT status, blocking_issues FROM content_pieces WHERE id=%s FOR UPDATE",
                (piece_id,),
            )
            piece = cursor.fetchone()
            if not piece:
                raise ValueError("La pieza no existe.")
            if not can_transition_content(piece["status"], new_status):
                raise ValueError("Ese cambio de estado no está permitido.")
            if new_status == "approved" and piece["blocking_issues"]:
                raise ValueError("Resuelve los bloqueos antes de aprobar la pieza.")
            if new_status == "approved":
                cursor.execute(
                    "SELECT count(*) AS pending FROM content_assets "
                    "WHERE piece_id=%s AND status='pending_review'", (piece_id,),
                )
                if cursor.fetchone()["pending"]:
                    raise ValueError("Revisa las imágenes generadas antes de aprobar la pieza.")
            cursor.execute(
                "UPDATE content_pieces SET status=%s, updated_at=now() WHERE id=%s",
                (new_status, piece_id),
            )
            cursor.execute(
                """
                INSERT INTO content_reviews
                    (piece_id, reviewer, decision, comment, previous_status, new_status)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (piece_id, actor, new_status, comment, piece["status"], new_status),
            )

    def list_reviews(self, piece_id):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM content_reviews WHERE piece_id=%s ORDER BY created_at DESC",
                (piece_id,),
            )
            return cursor.fetchall()

    def save_image_asset(self, piece_id, prompt, generated, actor):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM content_pieces WHERE id=%s", (piece_id,))
            if not cursor.fetchone():
                raise ValueError("La pieza no existe.")
            cursor.execute(
                """
                INSERT INTO content_assets
                    (piece_id, kind, provider, model, prompt, mime_type, content, created_by)
                VALUES (%s,'image','google-gemini',%s,%s,%s,%s,%s) RETURNING id
                """,
                (piece_id, generated.model, prompt, generated.mime_type, generated.data, actor),
            )
            return cursor.fetchone()["id"]

    def list_image_assets(self, piece_id):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, provider, model, prompt, mime_type, status, reviewer, reviewed_at, created_by, created_at "
                "FROM content_assets WHERE piece_id=%s AND kind='image' ORDER BY created_at DESC",
                (piece_id,),
            )
            return cursor.fetchall()

    def get_image_asset(self, asset_id):
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, mime_type, content FROM content_assets WHERE id=%s AND kind='image'",
                (asset_id,),
            )
            return cursor.fetchone()

    def review_image_asset(self, asset_id, status, reviewer):
        if status not in {"approved", "rejected"}:
            raise ValueError("La decisión sobre la imagen no es válida.")
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE content_assets SET status=%s, reviewer=%s, reviewed_at=now() "
                "WHERE id=%s AND status='pending_review' RETURNING piece_id",
                (status, reviewer, asset_id),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("La imagen no existe o ya fue revisada.")
            return row["piece_id"]
