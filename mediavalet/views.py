import io
import json
import os
import unicodedata
import urllib.parse

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render
from PIL import Image as PILImage

from images.models import CigionlineImage

# Allowed hostnames for image downloads (SSRF protection).
# Override via MEDIAVALET_ALLOWED_HOSTNAMES in settings.
_DEFAULT_ALLOWED_HOSTNAMES = [
    'mediavalet.com',
    '.mediavalet.com',
    'mediavaletcdn.com',
    '.mediavaletcdn.com',
]

MAX_IMAGE_BYTES = 50 * 1024 * 1024  # 50 MB


def _allowed_hostnames():
    return getattr(settings, 'MEDIAVALET_ALLOWED_HOSTNAMES', _DEFAULT_ALLOWED_HOSTNAMES)


def _is_valid_mediavalet_url(url: str) -> bool:
    """Return True only for https:// URLs on an allowed MediaValet hostname."""
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return False
    if parsed.scheme != 'https':
        return False
    hostname = (parsed.hostname or '').lower()
    if not hostname:
        return False
    for allowed in _allowed_hostnames():
        allowed = allowed.lower()
        if allowed.startswith('.'):
            if hostname.endswith(allowed) or hostname == allowed.lstrip('.'):
                return True
        else:
            if hostname == allowed or hostname.endswith('.' + allowed):
                return True
    return False


def _safe_filename(name: str) -> str:
    """Return a filesystem-safe version of a filename."""
    # Normalise unicode, replace path separators
    name = unicodedata.normalize('NFKD', name)
    name = name.replace('/', '_').replace('\\', '_').replace('\x00', '')
    # Keep only the basename
    name = os.path.basename(name) or 'image'
    return name[:255]


def asset_picker_view(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        from wagtail.admin.auth import permission_denied
        return permission_denied(request)

    base_url = getattr(settings, 'MEDIAVALET_ASSET_PICKER_URL', 'https://assetpicker.mediavalet.com')
    picker_url = (
        f'{base_url}'
        '?allowedAssetTypes=Image'
        '&allowedFeatures=cdnLink'
        '&redirectType=popup'
    )

    return render(request, 'mediavalet/asset_picker.html', {
        'picker_url': picker_url,
    })


def import_asset_view(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    file_url = (data.get('file_url') or '').strip()
    title = (data.get('title') or '').strip()
    file_name = _safe_filename((data.get('file_name') or '').strip() or 'mediavalet-image')

    if not _is_valid_mediavalet_url(file_url):
        return JsonResponse({'error': 'URL is not from an allowed MediaValet domain'}, status=400)

    # Download the image with a size cap.
    try:
        response = requests.get(
            file_url,
            timeout=30,
            stream=True,
            allow_redirects=True,
            headers={'User-Agent': 'CIGIOnline-MediaValet-Importer/1.0'},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return JsonResponse({'error': f'Download failed: {exc}'}, status=502)

    # After any CDN redirects, re-validate the final URL.
    if not _is_valid_mediavalet_url(response.url):
        return JsonResponse({'error': 'Redirected to an unauthorized domain'}, status=400)

    content_type = response.headers.get('Content-Type', '')
    if not content_type.startswith('image/'):
        return JsonResponse({'error': 'Response is not an image'}, status=400)

    buffer = io.BytesIO()
    for chunk in response.iter_content(chunk_size=8192):
        buffer.write(chunk)
        if buffer.tell() > MAX_IMAGE_BYTES:
            return JsonResponse({'error': 'Image exceeds maximum allowed size (50 MB)'}, status=400)

    image_data = buffer.getvalue()

    # Read dimensions from the in-memory bytes before any file-system/storage
    # write. _set_image_file_metadata() can't reliably re-open the file after
    # cloud storage closes it (same issue as generate_rendition_file).
    try:
        pil_img = PILImage.open(io.BytesIO(image_data))
        pil_img.verify()  # catch truncated files early
    except Exception as exc:
        return JsonResponse({'error': f'Not a valid image: {exc}'}, status=400)

    pil_img = PILImage.open(io.BytesIO(image_data))
    width, height = pil_img.size

    image = CigionlineImage(
        title=title or file_name,
        uploaded_by_user=request.user,
        width=width,
        height=height,
    )
    image.file.save(file_name, ContentFile(image_data), save=False)
    # Set file_size and file_hash; dimensions are already populated above.
    image._set_image_file_metadata()
    # Guarantee dimensions survive even if _set_image_file_metadata resets them.
    image.width = width
    image.height = height
    image.save()

    return JsonResponse({
        'success': True,
        'image_id': image.pk,
        'title': image.title,
    })
