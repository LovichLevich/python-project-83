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
from page_analyzer.utils import (
    get_metadata,
    normalize_url,
    tuple_to_dict,
)
from validators import url as validate_url # type: ignore
from dotenv import load_dotenv # type: ignore
from page_analyzer.db import (
    get_db_connection,
    get_url_name_by_id,
    add_url,
    find_url_id,
    get_all_urls,
    get_url_by_id,
    get_url_checks,
    add_url_check,
)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@app.errorhandler(Exception)
def handle_general_error(error):
    logging.exception("Произошла непредвиденная ошибка.")
    return redirect(url_for("index")), 500


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

    with get_db_connection() as conn:
        result = add_url(conn, normalized_url)
        if result:
            flash("Страница успешно добавлена", "success")
            return redirect(url_for("url_detail", url_id=result[0]))

        url_id = find_url_id(conn, normalized_url)[0]
        flash("Страница уже существует", "warning")
        return redirect(url_for("url_detail", url_id=url_id))


@app.route("/urls", methods=["GET"])
def urls():
    with get_db_connection() as conn:
        sites = get_all_urls(conn)
    return render_template("index_urls.html", sites=sites)


@app.route("/urls/<int:url_id>", methods=["GET"])
def url_detail(url_id):
    with get_db_connection() as conn:
        row = get_url_by_id(conn, url_id)
        if not row:
            flash("URL не найден.", "danger")
            return redirect(url_for("urls")), 422

        url = tuple_to_dict(conn, row)
        checks = [tuple_to_dict(conn, check) for check in get_url_checks(conn, url_id)]
    
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
