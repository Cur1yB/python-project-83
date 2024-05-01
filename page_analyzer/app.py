from flask import Flask, request, render_template, redirect, url_for, flash
from .db import get_db_connection
import validators
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if validators.url(url):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                        (url, datetime.now()))
            conn.commit()
            cur.close()
            conn.close()
            flash('URL добавлен успешно!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный URL.', 'danger')

    return render_template('index.html')


@app.route('/urls')
def urls():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls ORDER BY created_at DESC')
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
    cur.close()
    conn.close()
    return render_template('url_details.html', url=url_data)
