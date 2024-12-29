import psycopg2  # type: ignore
from psycopg2 import sql  # type: ignore
import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def normalize_url(url_name):
    parsed_url = urlparse(url_name)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def tuple_to_dict(cursor, row):
    return {cursor.description[i][0]: value for i, value in enumerate(row)}


def insert_url(cursor, normalized_url):
    cursor.execute(
        sql.SQL(
            """
            INSERT INTO urls (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
            """
        ),
        [normalized_url],
    )
    return cursor.fetchone()


def find_url_id(cursor, normalized_url):
    cursor.execute("SELECT id FROM urls WHERE name = %s", [normalized_url])
    return cursor.fetchone()


def fetch_all_urls(cursor):
    cursor.execute("""
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


def fetch_url_by_id(cursor, url_id):
    cursor.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
    return cursor.fetchone()


def fetch_url_checks(cursor, url_id):
    cursor.execute(
        "SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC",
        (url_id,),
    )
    return cursor.fetchall()


def insert_url_check(cursor, url_id, metadata):
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


def fetch_url_name_by_id(cursor, url_id):
    cursor.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
    row = cursor.fetchone()
    return row[0] if row else None
