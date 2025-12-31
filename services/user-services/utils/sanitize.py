import re
import html
from typing import Optional


def sanitize_string(value: str, max_length: int = 1000) -> str:
    if not value:
        return value

    value = value[:max_length]

    value = html.escape(value)

    value = re.sub(r'<[^>]+>', '', value)

    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    value = re.sub(r'on\w+\s*=', '', value, flags=re.IGNORECASE)

    value = value.strip()

    return value


def sanitize_html(value: str, max_length: int = 5000) -> str:
    if not value:
        return value

    value = value[:max_length]

    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r'<style[^>]*>.*?</style>', '', value, flags=re.IGNORECASE | re.DOTALL)

    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    value = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
    value = re.sub(r'on\w+\s*=\s*[^\s>]+', '', value, flags=re.IGNORECASE)

    return value.strip()


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename[:255]
    return filename
