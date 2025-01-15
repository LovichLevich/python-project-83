import logging
import os

from dotenv import load_dotenv  # type: ignore
from flask import (  # type: ignore
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from validators import url as validate_url  # type: ignore

from page_analyzer.db import (
    add_url,
    add_url_check,
    find_url_id,
    get_all_urls,
    get_db_connection,
    get_url_by_id,
    get_url_checks,
    get_url_name_by_id,
)
from page_analyzer.url_handling import normalize_url, url_length_check
from page_analyzer.utils import get_metadata

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


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
    if url_length_check(normalized_url):
        flash("URL слишком длинный.", "danger")
        return render_template("index.html"), 422

    with get_db_connection() as conn:
        existing_url = find_url_id(conn, normalized_url)
        if existing_url is not None:
            flash("Страница уже существует", "warning")
            return redirect(url_for("url_detail", url_id=existing_url))

        url_id = add_url(conn, normalized_url)
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("url_detail", url_id=url_id))


@app.route("/urls", methods=["GET"])
def urls():
    with get_db_connection() as conn:
        sites = get_all_urls(conn)
    return render_template("index_urls.html", sites=sites)


@app.route("/urls/<int:url_id>", methods=["GET"])
def url_detail(url_id):
    with get_db_connection() as conn:
        url = get_url_by_id(conn, url_id)
        if not url:
            flash("URL не найден.", "danger")
            return redirect(url_for("urls")), 404
        checks = get_url_checks(conn, url_id)
    return render_template("url_detail.html", url=url, checks=checks)


@app.route("/run_check/<int:url_id>", methods=["POST"])
def run_check(url_id):
    with get_db_connection() as conn:
        url_name = get_url_name_by_id(conn, url_id)
        if not url_name:
            flash("URL не найден в базе данных.", "danger")
            return redirect(url_for("index")), 422

        metadata = get_metadata(url_name)
        if metadata is None:
            flash("Произошла ошибка при проверке", "danger")
            return redirect(url_for("url_detail", url_id=url_id))

        add_url_check(conn, url_id, metadata)
        flash("Страница успешно проверена!", "success")
    return redirect(url_for("url_detail", url_id=url_id))


if __name__ == "__main__":
    app.run(debug=True)
