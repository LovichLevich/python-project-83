from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
from urllib.parse import urlparse
import os
import psycopg2  # type: ignore

DATABASE_URL = os.getenv('DATABASE_URL')


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


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def normalize_url(url_name):
    parsed_url = urlparse(url_name)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def tuple_to_dict(cursor, row):
    return {cursor.description[i][0]: value for i, value in enumerate(row)}
