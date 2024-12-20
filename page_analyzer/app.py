import os
import psycopg2  # type: ignore
from urllib.parse import urlparse
from flask import (  # type: ignore
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for
)
from psycopg2 import sql  # type: ignore
from dotenv import load_dotenv  # type: ignore
from validators import url as validate_url  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def normalize_url(url_name):
    """Normalize the URL by keeping only the scheme and netloc."""
    parsed_url = urlparse(url_name)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def tuple_to_dict(cursor, row):
    return {cursor.description[i][0]: value for i, value in enumerate(row)}


def fetch_metadata(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        h1 = soup.find('h1').text.strip() if soup.find('h1') else ''
        title = soup.find('title').text.strip() if soup.find('title') else ''
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = (
            description_tag['content'].strip()
            if description_tag else ''
        )

        return {
            'status_code': response.status_code,
            'h1': h1,
            'title': title,
            'description': description
        }
    except requests.RequestException:
        return None


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


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url_name = request.form.get("url", "").strip()

        if not validate_url(url_name):
            flash("Некорректный URL.", "danger")
            return render_template("index.html")

        normalized_url = normalize_url(url_name)

        if len(normalized_url) > 255:
            flash("URL слишком длинный.", "danger")
            return render_template("index.html")

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                try:
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
                    result = cursor.fetchone()
                    conn.commit()

                    if result:
                        flash("Страница успешно добавлена", "success")
                        return redirect(url_for
                                        ("url_detail", url_id=result[0]))

                    cursor.execute("SELECT id FROM urls WHERE name = %s",
                                   [normalized_url]
                                   )
                    url_id = cursor.fetchone()[0]
                    flash("Страница уже существует", "warning")
                    return redirect(url_for("url_detail", url_id=url_id))

                except Exception as e:
                    flash(f"Ошибка базы данных: {e}", "danger")
                    return render_template("index.html")

    return render_template("index.html")


@app.route("/urls", methods=["GET"])
def urls():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
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
            sites = cursor.fetchall()

    return render_template("index_urls.html", sites=sites)


@app.route("/urls/<int:url_id>", methods=["GET"])
def url_detail(url_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
                row = cursor.fetchone()
                if not row:
                    flash("URL не найден.", "danger")
                    return redirect(url_for("urls"))

                url = tuple_to_dict(cursor, row)
                cursor.execute(
                    "SELECT * FROM url_checks WHERE url_id = %s" 
                    "ORDER BY created_at DESC",
                    (url_id,))
                checks = ([tuple_to_dict(cursor, row)
                           for row in cursor.fetchall()])

        return render_template("url_detail.html", url=url, checks=checks)
    except Exception as e:
        logging.error(f"Error fetching URL details: {e}")
        flash(f"Произошла ошибка: {e}", "danger")
        return redirect(url_for("urls"))


@app.route("/run_check/<int:url_id>", methods=["POST"])
def run_check(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
            row = cursor.fetchone()
            if not row:
                flash("URL не найден в базе данных.", "danger")
                return redirect(url_for("index"))

            metadata = fetch_metadata(row[0])

            if metadata is None:
                flash("Произошла ошибка при проверке", "danger")
                return redirect(url_for("url_detail", url_id=url_id))

            try:
                insert_url_check(cursor, url_id, metadata)
                conn.commit()

                flash("Страница успешно проверена!", "success")
            except Exception as e:
                flash(f"Ошибка базы данных: {e}", "danger")
                logging.error(f"Ошибка базы данных: {e}")

    return redirect(url_for("url_detail", url_id=url_id))


if __name__ == "__main__":
    app.run(debug=True)
