import io
import json
import os
import unicodedata
import urllib.parse

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.text import get_valid_filename
from PIL import Image as PILImage
from wagtail.images.permissions import permission_policy

from images.models import CigionlineImage


_DEFAULT_ALLOWED_HOSTNAMES = [
    "mediavalet.com",
    ".mediavalet.com",
    "mediavaletcdn.com",
    ".mediavaletcdn.com",
]
MAX_IMAGE_BYTES = 50 * 1024 * 1024
MAX_REDIRECTS = 5


class UnsafeMediaValetURL(ValueError):
    pass


def get_asset_picker_url():
    base_url = getattr(
        settings,
        "MEDIAVALET_ASSET_PICKER_URL",
        "https://assetpicker.mediavalet.com",
    )
    parsed_url = urllib.parse.urlsplit(base_url)
    query = dict(urllib.parse.parse_qsl(parsed_url.query, keep_blank_values=True))
    query.update(
        {
            "allowedAssetTypes": "Image",
            "allowedFeatures": "cdnLink",
            "redirectType": "popup",
        }
    )

    app_id = getattr(settings, "MEDIAVALET_ASSET_PICKER_APP_ID", "")
    if app_id:
        query["appId"] = app_id

    return urllib.parse.urlunsplit(
        parsed_url._replace(query=urllib.parse.urlencode(query))
    )


def get_asset_picker_origin():
    parsed = urllib.parse.urlsplit(get_asset_picker_url())
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


def _allowed_hostnames():
    return getattr(
        settings,
        "MEDIAVALET_ALLOWED_HOSTNAMES",
        _DEFAULT_ALLOWED_HOSTNAMES,
    )


def _is_valid_mediavalet_url(url: str) -> bool:
    """Allow HTTPS downloads only from configured MediaValet hostnames."""
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return False
    if parsed.scheme != "https":
        return False
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return False
    for allowed in _allowed_hostnames():
        allowed = allowed.lower()
        if allowed.startswith("."):
            if hostname.endswith(allowed) or hostname == allowed.lstrip("."):
                return True
        elif hostname == allowed or hostname.endswith("." + allowed):
            return True
    return False


def _safe_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    return (get_valid_filename(os.path.basename(name)) or "image")[:255]


def _can_import(user) -> bool:
    return bool(
        user.is_authenticated
        and user.is_active
        and user.is_staff
        and permission_policy.user_has_permission(user, "add")
    )


def _download_image(url: str):
    """Fetch an allowed URL, validating each redirect before following it."""
    for _ in range(MAX_REDIRECTS + 1):
        if not _is_valid_mediavalet_url(url):
            raise UnsafeMediaValetURL(
                "URL is not from an allowed MediaValet domain"
            )

        response = requests.get(
            url,
            timeout=30,
            stream=True,
            allow_redirects=False,
            headers={"User-Agent": "CIGIOnline-MediaValet-Importer/1.0"},
        )
        if response.is_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise requests.RequestException("Redirect response has no location")
            url = urllib.parse.urljoin(url, location)
            continue

        try:
            response.raise_for_status()
        except Exception:
            response.close()
            raise
        return response

    raise UnsafeMediaValetURL("Too many redirects")


def asset_picker_view(request):
    if not _can_import(request.user):
        from wagtail.admin.auth import permission_denied

        return permission_denied(request)

    return render(
        request,
        "mediavalet/asset_picker.html",
        {
            "picker_url": get_asset_picker_url(),
            "picker_origin": get_asset_picker_origin(),
        },
    )


def import_asset_view(request):
    if not _can_import(request.user):
        return JsonResponse({"error": "Forbidden"}, status=403)
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON object"}, status=400)

    file_url = data.get("file_url", "")
    title = data.get("title", "")
    file_name = data.get("file_name", "")
    if not all(isinstance(value, str) for value in (file_url, title, file_name)):
        return JsonResponse({"error": "Invalid asset data"}, status=400)
    file_url = file_url.strip()
    title = title.strip()[:255]
    file_name = _safe_filename(file_name.strip() or "mediavalet-image")

    try:
        response = _download_image(file_url)
    except UnsafeMediaValetURL as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except requests.RequestException as exc:
        return JsonResponse({"error": f"Download failed: {exc}"}, status=502)

    try:
        content_type = response.headers.get("Content-Type", "").lower()
        if not content_type.startswith("image/"):
            return JsonResponse({"error": "Response is not an image"}, status=400)

        try:
            content_length = int(response.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length > MAX_IMAGE_BYTES:
            return JsonResponse(
                {"error": "Image exceeds maximum allowed size (50 MB)"},
                status=400,
            )

        buffer = io.BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            buffer.write(chunk)
            if buffer.tell() > MAX_IMAGE_BYTES:
                return JsonResponse(
                    {"error": "Image exceeds maximum allowed size (50 MB)"},
                    status=400,
                )
        image_data = buffer.getvalue()
    finally:
        response.close()

    try:
        pil_img = PILImage.open(io.BytesIO(image_data))
        pil_img.verify()
        pil_img = PILImage.open(io.BytesIO(image_data))
        width, height = pil_img.size
    except Exception as exc:
        return JsonResponse({"error": f"Not a valid image: {exc}"}, status=400)

    collection = (
        permission_policy.collections_user_has_permission_for(request.user, "add")
        .order_by("path")
        .first()
    )
    if not collection:
        return JsonResponse({"error": "Forbidden"}, status=403)

    image = CigionlineImage(
        title=title or file_name,
        uploaded_by_user=request.user,
        collection=collection,
        width=width,
        height=height,
    )
    try:
        image.file.save(file_name, ContentFile(image_data), save=False)
        image._set_image_file_metadata()
        image.width = width
        image.height = height
        image.save()
    except Exception:
        if image.file.name:
            image.file.delete(save=False)
        raise

    return JsonResponse(
        {"success": True, "image_id": image.pk, "title": image.title}
    )


def image_data_view(request, image_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)

    image = get_object_or_404(CigionlineImage, pk=image_id)
    if not permission_policy.user_has_permission_for_instance(
        request.user, "choose", image
    ):
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        rendition = image.get_rendition("max-165x165")
        preview = {
            "url": rendition.url,
            "width": rendition.width,
            "height": rendition.height,
        }
    except Exception:
        preview = None

    try:
        edit_link = reverse("wagtailimages:edit", args=[image.pk])
    except Exception:
        edit_link = ""

    data = {
        "id": str(image.pk),
        "string": image.title,
        "title": image.title,
        "edit_url": edit_link,
        "edit_link": edit_link,
        "default_alt_text": image.default_alt_text,
    }
    if preview:
        data["preview"] = preview
    return JsonResponse(data)
