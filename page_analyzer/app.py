from flask import Flask, request, render_template, redirect, url_for, flash
from .db import (open_db_connection, close_db_connection, get_url_by_id,
                 fetch_and_parse_url, insert_url_check)
import validators
from datetime import datetime
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, urlunparse

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')


def format_date(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    return value.strftime(format)


app.jinja_env.filters['date'] = format_date


def normalize_url(input_url):
    url_parts = urlparse(input_url)
    normalized_url = urlunparse((url_parts.scheme, url_parts.netloc, '', '', '', ''))
    return normalized_url


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
    if validators.url(raw_url):
        normalized_url = normalize_url(raw_url)
        conn, cur = open_db_connection()
        try:
            cur.execute('SELECT id FROM urls WHERE name = %s', (normalized_url,))
            existing_url = cur.fetchone()
            if existing_url:
                flash('Страница уже существует', 'alert-info')
                return redirect(url_for('url_details', id=existing_url['id']))
            else:
                cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id',
                            (normalized_url, datetime.now()))
                url_id = cur.fetchone()['id']
                conn.commit()
                flash('Страница успешно добавлена', 'alert-success')
                return redirect(url_for('url_details', id=url_id))
        except Exception as e:
            conn.rollback()
            flash(f'Произошла ошибка при добавлении URL: {e}', 'alert-danger')
        finally:
            close_db_connection(conn, cur)
    else:
        flash('Некорректный URL', 'alert-danger')
        return render_template('index.html'), 422


@app.route('/urls')
def urls():
    conn, cur = open_db_connection()
    cur.execute('''
        SELECT u.id, u.name, MAX(c.created_at) AS last_checked, MAX(c.status_code) AS last_status_code
        FROM urls u
        LEFT JOIN url_checks c ON u.id = c.url_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    urls_data = cur.fetchall()
    close_db_connection(conn, cur)
    return render_template('urls.html', urls=urls_data)


@app.route('/urls/<int:id>')
def url_details(id):
    conn, cur = open_db_connection()
    cur.execute('SELECT * FROM urls WHERE id = %s', (id,))
    url_data = cur.fetchone()
    cur.execute('SELECT * FROM url_checks WHERE url_id = %s '
                + 'ORDER BY created_at DESC', (id,))
    checks = cur.fetchall()
    close_db_connection(conn, cur)
    return render_template('url.html', url=url_data, checks=checks)
