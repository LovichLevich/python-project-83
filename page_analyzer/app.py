import logging
import os
from flask import (  # type: ignore
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from page_analyzer.utils import fetch_metadata
from validators import url as validate_url  # type: ignore
from db import (
    fetch_url_name_by_id,
    get_db_connection,
    normalize_url,
    tuple_to_dict,
    insert_url,
    find_url_id,
    fetch_all_urls,
    fetch_url_by_id,
    fetch_url_checks,
    insert_url_check,
)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/urls", methods=["POST"])
def start():
    url_name = request.form.get("url", "").strip()
    if not validate_url(url_name):
        flash("Некорректный URL.", "danger")
        return render_template("index.html"), 422

    normalized_url = normalize_url(url_name)
    if len(normalized_url) > 255:
        flash("URL слишком длинный.", "danger")
        return render_template("index.html"), 422

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                result = insert_url(cursor, normalized_url)
                if result:
                    conn.commit()
                    flash("Страница успешно добавлена", "success")
                    return redirect(url_for("url_detail", url_id=result[0]))

                url_id = find_url_id(cursor, normalized_url)[0]
                conn.commit()
                flash("Страница уже существует", "warning")
                return redirect(url_for("url_detail", url_id=url_id))
    except Exception as e:
        flash(f"Ошибка базы данных: {e}", "danger")
        return render_template("index.html")


@app.route("/urls", methods=["GET"])
def urls():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sites = fetch_all_urls(cursor)
        conn.commit()
    return render_template("index_urls.html", sites=sites)


@app.route("/urls/<int:url_id>", methods=["GET"])
def url_detail(url_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                row = fetch_url_by_id(cursor, url_id)
                if not row:
                    flash("URL не найден.", "danger")
                    return redirect(url_for("urls")), 422

                url = tuple_to_dict(cursor, row)
                checks = [tuple_to_dict(cursor, row)
                          for row in fetch_url_checks(cursor, url_id)]
        return render_template("url_detail.html", url=url, checks=checks)
    except Exception as e:
        logging.error(f"Ошибка при получении сведений об URL-адресе: {e}")
        flash(f"Произошла ошибка: {e}", "danger")
        return redirect(url_for("urls")), 500


@app.route("/run_check/<int:url_id>", methods=["POST"])
def run_check(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            url_name = fetch_url_name_by_id(cursor, url_id)
            if not url_name:
                flash("URL не найден в базе данных.", "danger")
                return redirect(url_for("index")), 422

            metadata = fetch_metadata(url_name)
            if metadata is None:
                flash("Произошла ошибка при проверке", "danger")
                return redirect(url_for("url_detail", url_id=url_id))

            try:
                insert_url_check(cursor, url_id, metadata)
                conn.commit()
                flash("Страница успешно проверена!", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Ошибка базы данных: {e}", "danger")
                logging.error(f"Ошибка базы данных: {e}")
    return redirect(url_for("url_detail", url_id=url_id))


if __name__ == "__main__":
    app.run(debug=True)
