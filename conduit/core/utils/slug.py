from secrets import token_urlsafe

from slugify import slugify


def create_slug(title: str) -> str:
    slug = slugify(text=title, max_length=24, lowercase=True)
    unique_code = token_urlsafe(16)
    return f"{slug}-{unique_code.lower()}"
