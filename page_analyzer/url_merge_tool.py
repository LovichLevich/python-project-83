def merge_urls_checks(urls, url_checks):
    checks_dict = {item["id"]: item for item in url_checks}
    merged = []
    for url in urls:
        check = checks_dict.get(url["id"], {})
        merged.append({**url, **check})
    return merged