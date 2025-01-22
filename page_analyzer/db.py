from contextlib import contextmanager

import psycopg2  # type: ignore
from psycopg2.extras import DictCursor  # type: ignore


@contextmanager
def get_db_connection(database_url):
    conn = psycopg2.connect(database_url)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def add_url(conn, normalized_url):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(
            """
            INSERT INTO urls (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
            """,
            [normalized_url],
        )
        result = cursor.fetchone()
        return result["id"] if result else None


def find_url_id(conn, normalized_url):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT id FROM urls WHERE name = %s", [normalized_url])
        result = cursor.fetchone()
        return result["id"] if result else None


def get_all_urls(conn):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT DISTINCT ON (urls.id, urls.name)
                urls.id,
                urls.name,
                url_checks.created_at,
                url_checks.status_code
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            ORDER BY urls.id DESC, urls.name, url_checks.created_at DESC;
        """)
        return cursor.fetchall()


def get_url_id(conn, url_id):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
        return cursor.fetchone()


def get_url_checks(conn, url_id):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(
            """SELECT * FROM url_checks
            WHERE url_id = %s
            ORDER BY created_at DESC""",
            (url_id,),
        )
        return cursor.fetchall()


def add_url_check(conn, url_id, metadata):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(
            """
            INSERT INTO
            url_checks (url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                url_id,
                metadata["status_code"],
                metadata["h1"],
                metadata["title"],
                metadata["description"],
            ),
        )
