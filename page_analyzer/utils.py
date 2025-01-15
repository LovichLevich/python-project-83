import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore


def get_metadata(url):
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
