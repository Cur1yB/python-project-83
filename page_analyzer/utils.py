from urllib.parse import urlparse, urlunparse


def format_date(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    return value.strftime(format)


def normalize_url(input_url):
    url_parts = urlparse(input_url)
    normalized_url = urlunparse((url_parts.scheme, url_parts.netloc, '', '', '', ''))
    return normalized_url
