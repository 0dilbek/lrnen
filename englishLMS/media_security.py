from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core import signing


SALT = 'english-lms-protected-media-v1'
PROTECTED_STATIC_PREFIXES = ('book/', 'book2/', 'book3/', 'coursebooks/', 'audio/')


def _source_for_url(url):
    if not isinstance(url, str):
        return None
    path = url.split('?', 1)[0]
    media_prefix = '/' + settings.MEDIA_URL.strip('/') + '/'
    static_prefix = '/' + settings.STATIC_URL.strip('/') + '/'
    if path.startswith(media_prefix):
        return 'media', path[len(media_prefix):]
    if path.startswith(static_prefix):
        relative = path[len(static_prefix):]
        if relative.startswith(PROTECTED_STATIC_PREFIXES):
            return 'static', relative
    return None


def protected_media_url(url):
    source = _source_for_url(url)
    if not source:
        return url
    root, relative = source
    token = signing.dumps({'root': root, 'path': relative}, salt=SALT, compress=True)
    return f'/api/media/access/{token}/'


def resolve_protected_token(token):
    payload = signing.loads(token, salt=SALT, max_age=settings.PROTECTED_MEDIA_URL_TTL)
    root = payload.get('root')
    relative = str(PurePosixPath(payload.get('path', '')))
    if not relative or relative.startswith('../') or relative == '..':
        raise signing.BadSignature('Invalid path')

    if root == 'media':
        base = Path(settings.MEDIA_ROOT).resolve()
    elif root == 'static' and relative.startswith(PROTECTED_STATIC_PREFIXES):
        base = (Path(settings.BASE_DIR) / 'static').resolve()
    else:
        raise signing.BadSignature('Invalid media root')

    target = (base / relative).resolve()
    if base not in target.parents or not target.is_file():
        raise signing.BadSignature('Media not found')
    return root, relative, target


def protect_content_urls(value):
    if isinstance(value, dict):
        return {key: protect_content_urls(item) for key, item in value.items()}
    if isinstance(value, list):
        return [protect_content_urls(item) for item in value]
    if isinstance(value, str):
        return protected_media_url(value)
    return value
