from flask import Flask, request, render_template, redirect, url_for, flash
from .db import get_db_connection
import validators
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT name FROM urls WHERE id = %s', (id,))
    url = cur.fetchone()['name']

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title').text if soup.find('title') else None
            h1 = soup.find('h1').text if soup.find('h1') else None
            description = soup.find('meta', attrs={'name': 'description'})
            description = description['content'] if description else None
            cur.execute(
                'INSERT INTO url_checks (url_id, status_code, h1, title, '
                + 'description, created_at) VALUES (%s, %s, %s, %s, %s, %s)',
                (id, response.status_code, h1, title, description,
                 datetime.now())
            )
            conn.commit()
            flash('Страница успешно проверена', 'success')
        else:
            flash('Ошибка при запросе страницы', 'danger')
    except requests.RequestException as e:
        flash(f'Произошла ошибка при проверке', 'danger')

    cur.close()
    conn.close()
    return redirect(url_for('url_details', id=id))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if validators.url(url):
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute('SELECT id FROM urls WHERE name = %s', (url,))
                existing_url = cur.fetchone()
                if existing_url:
                    flash('Страница уже существует', 'info')
                    return redirect(url_for('url_details', id=existing_url[0]))
                else:
                    cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id',
                                (url, datetime.now()))
                    url_id = cur.fetchone()[0]
                    conn.commit()
                    flash('Страница успешно добавлена', 'success')
                    return redirect(url_for('url_details', id=url_id))
            except Exception as e:
                conn.rollback()
                flash(f'Ошибка при добавлении URL: {e}', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Некорректный URL', 'danger')

    return render_template('index.html')


@app.route('/urls')
def urls():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT u.id, u.name, MAX(c.created_at) AS last_checked, MAX(c.status_code) AS last_status_code
        FROM urls u
        LEFT JOIN url_checks c ON u.id = c.url_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    urls_data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('urls.html', urls=urls_data)


@app.route('/urls/<int:id>')
def url_details(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls WHERE id = %s', (id,))
    url_data = cur.fetchone()
    cur.execute('SELECT * FROM url_checks WHERE url_id = %s '
                + 'ORDER BY created_at DESC', (id,))
    checks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('url_details.html', url=url_data, checks=checks)
