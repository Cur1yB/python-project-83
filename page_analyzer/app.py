from flask import Flask, request, render_template, redirect, url_for, flash
from .db import (open_db_connection, close_db_connection, get_url_by_id,
                 fetch_and_parse_url, insert_url_check, check_url_exists,
                 insert_new_url, get_all_urls, get_url_details)
import validators
from dotenv import load_dotenv
import os
from .utils import format_date, normalize_url


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.jinja_env.filters['date'] = format_date


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    conn = open_db_connection()[0]
    url = get_url_by_id(conn, id)

    if url:
        result = fetch_and_parse_url(url)
        if 'error' not in result:
            insert_url_check(conn, id, result)
            flash('Страница успешно проверена', 'alert-success')
        else:
            flash(result['error'], 'alert-danger')
    else:
        flash('URL не найден', 'alert-danger')

    close_db_connection(conn, None)
    return redirect(url_for('url_details', id=id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    raw_url = request.form['url']
    if not validators.url(raw_url):
        flash('Некорректный URL', 'alert-danger')
        return render_template('index.html'), 422

    normalized_url = normalize_url(raw_url)
    conn, cur = open_db_connection()
    try:
        existing_url = check_url_exists(cur, normalized_url)
        if existing_url:
            flash('Страница уже существует', 'alert-info')
            redirect_url = redirect(url_for('url_details', id=existing_url['id']))
        else:
            url_id = insert_new_url(cur, normalized_url)
            conn.commit()
            flash('Страница успешно добавлена', 'alert-success')
            redirect_url = redirect(url_for('url_details', id=url_id))
    except Exception as e:
        conn.rollback()
        flash(f'Произошла ошибка при добавлении URL: {e}', 'alert-danger')
        redirect_url = render_template('index.html'), 422
    finally:
        close_db_connection(conn, cur)

    return redirect_url


@app.route('/urls')
def urls():
    urls_data = get_all_urls()
    return render_template('urls.html', urls=urls_data)


@app.route('/urls/<int:id>')
def url_details(id):
    url_data, checks = get_url_details(id)
    return render_template('url.html', url=url_data, checks=checks)
