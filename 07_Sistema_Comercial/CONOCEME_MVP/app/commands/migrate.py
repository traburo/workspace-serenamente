import os
from pathlib import Path

import psycopg


def main():
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise SystemExit("DATABASE_URL no está configurada")
    migrations = sorted((Path(__file__).parents[2] / "migrations").glob("*.sql"))
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    filename text PRIMARY KEY,
                    applied_at timestamptz NOT NULL DEFAULT now()
                )
                """
            )
            for migration in migrations:
                cursor.execute(
                    "SELECT 1 FROM schema_migrations WHERE filename = %s",
                    (migration.name,),
                )
                if cursor.fetchone():
                    continue
                cursor.execute(migration.read_text(encoding="utf-8"), prepare=False)
                cursor.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s)",
                    (migration.name,),
                )
                print(f"Applied {migration.name}")


if __name__ == "__main__":
    main()
