from urllib.parse import urlparse


def normalize_url(url_name):
    parsed_url = urlparse(url_name)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def url_length_check(url, max_length=255):
    return len(url) > max_length
