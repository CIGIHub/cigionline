import io
import json
import os
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage

from images.models import CigionlineImage

from .views import (
    MAX_IMAGE_BYTES,
    UnsafeMediaValetURL,
    _download_image,
    _is_valid_mediavalet_url,
    get_asset_picker_origin,
    get_asset_picker_url,
    image_data_view,
    import_asset_view,
)
from .panels import MediaValetImageChooserPanel


def png_bytes():
    image = PILImage.new("RGB", (1, 1))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


PNG_BYTES = png_bytes()


class AssetPickerUrlTests(SimpleTestCase):
    @override_settings(MEDIAVALET_ASSET_PICKER_APP_ID="test-app-id")
    def test_includes_configured_app_id(self):
        self.assertEqual(
            get_asset_picker_url(),
            "https://assetpicker.mediavalet.com?allowedAssetTypes=Image&allowedFeatures=cdnLink&redirectType=popup&appId=test-app-id",
        )

    @override_settings(
        MEDIAVALET_ASSET_PICKER_URL="https://picker.example.test/path?existing=1",
        MEDIAVALET_ASSET_PICKER_APP_ID="",
    )
    def test_picker_origin_matches_configured_url(self):
        self.assertEqual(get_asset_picker_origin(), "https://picker.example.test")
        self.assertIn("existing=1", get_asset_picker_url())


class PanelCoverageTests(SimpleTestCase):
    def assert_mediavalet_fields(self, panels, expected_fields):
        def walk(items):
            for panel in items:
                yield panel
                yield from walk(getattr(panel, "children", []))

        panels_by_field = {
            panel.field_name: panel
            for panel in walk(panels)
            if getattr(panel, "field_name", None)
        }
        for field_name in expected_fields:
            self.assertIsInstance(
                panels_by_field[field_name],
                MediaValetImageChooserPanel,
                field_name,
            )

    def test_image_panels_use_mediavalet_chooser(self):
        from annual_reports.models import AnnualReportPage
        from articles.models import ArticlePage, ArticleSeriesPage, OpinionSeriesPage
        from core.models import (
            BasicPageAbstract,
            FeatureablePageAbstract,
            ShareablePageAbstract,
            SlidePage,
        )
        from events.models import EventPage
        from multimedia.models import MultimediaPage, MultimediaSeriesPage
        from people.models import PersonPage
        from promotions.models import PromotionBlock
        from publications.models import (
            PublicationPage,
            PublicationSeriesPage,
            T7PublicationPage,
        )
        from research.models import ProjectPage

        cases = [
            (AnnualReportPage.content_panels, {"image_poster"}),
            (
                ArticlePage.content_panels,
                {"image_hero", "image_poster", "image_banner", "image_banner_small"},
            ),
            (
                ArticleSeriesPage.content_panels,
                {"image_hero", "image_banner", "image_banner_small", "image_poster"},
            ),
            (OpinionSeriesPage.content_panels, {"image_hero", "image_banner"}),
            (EventPage.edit_handler.children, {"registration_image_banner"}),
            (
                MultimediaPage.content_panels,
                {"image_hero", "image_banner", "image_square", "image_poster"},
            ),
            (
                MultimediaSeriesPage.content_panels,
                {"image_hero", "image_banner", "image_poster", "image_logo"},
            ),
            (PersonPage.content_panels, {"image_square", "image_media"}),
            (PromotionBlock.panels, {"image_promotion", "image_promotion_small"}),
            (PublicationPage.content_panels, {"image_cover", "image_poster"}),
            (PublicationSeriesPage.content_panels, {"image_hero", "image_poster"}),
            (T7PublicationPage.content_panels, {"image_feature", "image_poster"}),
            (ProjectPage.content_panels, {"image_hero", "image_banner"}),
            (SlidePage.content_panels, {"image_background"}),
            (BasicPageAbstract.images_panel.children, {"image_hero", "image_banner"}),
            (FeatureablePageAbstract.feature_panel.children, {"image_feature"}),
            (ShareablePageAbstract.social_panel.children, {"image_social"}),
        ]
        for panels, fields in cases:
            with self.subTest(fields=fields):
                self.assert_mediavalet_fields(panels, fields)


class MediaValetDownloadTests(SimpleTestCase):
    def test_url_allowlist_rejects_lookalike_and_non_https_hosts(self):
        self.assertTrue(
            _is_valid_mediavalet_url("https://assets.mediavaletcdn.com/image.png")
        )
        self.assertFalse(
            _is_valid_mediavalet_url("https://mediavaletcdn.com.example.com/image.png")
        )
        self.assertFalse(
            _is_valid_mediavalet_url("http://assets.mediavaletcdn.com/image.png")
        )

    def test_redirect_target_is_validated_before_request(self):
        response = type(
            "Response",
            (),
            {
                "is_redirect": True,
                "headers": {"Location": "http://127.0.0.1/private"},
                "close": lambda self: None,
            },
        )()

        with patch("mediavalet.views.requests.get", return_value=response) as get_mock:
            with self.assertRaises(UnsafeMediaValetURL):
                _download_image("https://assets.mediavaletcdn.com/image.png")

        get_mock.assert_called_once()


class ImportAssetTests(TestCase):
    class Response:
        is_redirect = False

        def __init__(self, content_length=len(PNG_BYTES)):
            self.closed = False
            self.headers = {
                "Content-Type": "image/png",
                "Content-Length": str(content_length),
            }

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size=8192):
            yield PNG_BYTES

        def close(self):
            self.closed = True

    def make_request(self, user, data=None):
        request = RequestFactory().post(
            "/admin/mediavalet/import/",
            data=data
            or {
                "file_url": "https://assets.mediavaletcdn.com/image.png",
                "file_name": "image.png",
                "title": "Image",
            },
            content_type="application/json",
        )
        request.user = user
        return request

    def test_authorized_user_can_open_asset_picker(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("mediavalet_asset_picker"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MediaValet Asset Picker")
        self.assertContains(response, "assetpicker.mediavalet.com")

    def test_staff_without_image_add_permission_cannot_import(self):
        user = get_user_model().objects.create_user(
            username="staff",
            password="password",
            is_staff=True,
        )

        response = import_asset_view(self.make_request(user))

        self.assertEqual(response.status_code, 403)

    def test_import_rejects_non_string_asset_data(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )

        response = import_asset_view(
            self.make_request(
                user,
                {"file_url": 123, "file_name": "image.png", "title": "Image"},
            )
        )

        self.assertEqual(response.status_code, 400)

    def test_import_creates_image_and_closes_download(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        download = self.Response()

        with tempfile.TemporaryDirectory() as media_root:
            with (
                override_settings(MEDIA_ROOT=media_root),
                patch("mediavalet.views.requests.get", return_value=download),
            ):
                response = import_asset_view(self.make_request(user))
                image = CigionlineImage.objects.get()
                chooser_request = RequestFactory().get("/admin/mediavalet/image-data/")
                chooser_request.user = user
                chooser_response = image_data_view(chooser_request, image.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual((image.width, image.height), (1, 1))
        self.assertEqual(image.uploaded_by_user, user)
        self.assertTrue(download.closed)
        chooser_data = json.loads(chooser_response.content)
        self.assertEqual(chooser_data["id"], str(image.pk))
        self.assertIn("edit_url", chooser_data)
        self.assertIn("default_alt_text", chooser_data)
        self.assertEqual(chooser_data["preview"]["width"], 1)

    def test_import_rejects_oversized_image_and_closes_download(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        download = self.Response(MAX_IMAGE_BYTES + 1)

        with patch("mediavalet.views.requests.get", return_value=download):
            response = import_asset_view(self.make_request(user))

        self.assertEqual(response.status_code, 400)
        self.assertTrue(download.closed)
        self.assertFalse(CigionlineImage.objects.exists())

    def test_storage_file_is_deleted_if_database_save_fails(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )

        with tempfile.TemporaryDirectory() as media_root:
            with (
                override_settings(MEDIA_ROOT=media_root),
                patch("mediavalet.views.requests.get", return_value=self.Response()),
                patch.object(CigionlineImage, "save", side_effect=Exception("db down")),
            ):
                with self.assertRaises(Exception):
                    import_asset_view(self.make_request(user))

            stored_files = [
                filename
                for root, _, files in os.walk(media_root)
                for filename in files
            ]
            self.assertEqual(stored_files, [])
