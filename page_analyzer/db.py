import os
import psycopg2 # type: ignore

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def add_url(conn, normalized_url):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO urls (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
            """, [normalized_url])
        return cursor.fetchone()


def find_url_id(conn, normalized_url):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM urls WHERE name = %s", [normalized_url])
        return cursor.fetchone()


def get_all_urls(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                urls.id,
                urls.name,
                (SELECT created_at
                 FROM url_checks
                 WHERE url_checks.url_id = urls.id
                 ORDER BY created_at DESC
                 LIMIT 1) AS created_at,
                (SELECT status_code
                 FROM url_checks
                 WHERE url_checks.url_id = urls.id
                 ORDER BY created_at DESC
                 LIMIT 1) AS status_code
            FROM urls
            ORDER BY urls.id DESC;
            """)
        return cursor.fetchall()


def get_url_by_id(conn, url_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
        return cursor.fetchone()


def get_url_checks(conn, url_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC",
            (url_id,),
        )
        return cursor.fetchall()


def add_url_check(conn, url_id, metadata):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO url_checks (url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                url_id,
                metadata['status_code'],
                metadata['h1'],
                metadata['title'],
                metadata['description']
            )
        )


def get_url_name_by_id(conn, url_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
        row = cursor.fetchone()
        return row[0] if row else None
