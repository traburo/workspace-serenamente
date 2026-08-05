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
