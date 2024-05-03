import os
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from datetime import datetime


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = extras.DictCursor
    return conn


def open_db_connection():
    conn = get_db_connection()
    cur = conn.cursor()
    return conn, cur


def close_db_connection(conn, cur):
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
        

def get_url_by_id(conn, id):
    """ Получает URL по идентификатору. """
    cur = conn.cursor()
    cur.execute('SELECT name FROM urls WHERE id = %s', (id,))
    result = cur.fetchone()
    cur.close()
    return result['name'] if result else None


def fetch_and_parse_url(url):
    """ Запрашивает URL и анализирует его содержимое. """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return {
                'title': soup.find('title').text if soup.find('title') else None,
                'h1': soup.find('h1').text if soup.find('h1') else None,
                'description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else None,
                'status_code': response.status_code
            }
    except requests.RequestException:
        return {'error': 'Произошла ошибка при проверке'}


def insert_url_check(conn, url_id, data):
    """ Вставляет результаты проверки URL в базу данных. """
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (url_id, data['status_code'], data['h1'], data['title'], data['description'], datetime.now())
    )
    conn.commit()
    cur.close()
