import io
import os
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from PIL import Image as PILImage

from images.models import CigionlineImage

from .views import get_asset_picker_url, import_asset_view


def png_bytes():
    image = PILImage.new('RGB', (1, 1))
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


PNG_BYTES = png_bytes()


class AssetPickerUrlTests(TestCase):
    @override_settings(MEDIAVALET_ASSET_PICKER_APP_ID='test-app-id')
    def test_includes_configured_app_id(self):
        self.assertEqual(
            get_asset_picker_url(),
            'https://assetpicker.mediavalet.com?allowedAssetTypes=Image&allowedFeatures=cdnLink&redirectType=popup&appId=test-app-id',
        )

    @override_settings(MEDIAVALET_ASSET_PICKER_APP_ID='')
    def test_omits_blank_app_id(self):
        self.assertNotIn('appId=', get_asset_picker_url())


class ImportAssetTests(TestCase):
    def test_storage_file_is_deleted_if_database_save_fails(self):
        class Response:
            url = 'https://assets.mediavaletcdn.com/image.png'
            headers = {'Content-Type': 'image/png'}

            def raise_for_status(self):
                pass

            def iter_content(self, chunk_size=8192):
                yield PNG_BYTES

        user = get_user_model().objects.create_user(
            username='staff',
            password='password',
            is_staff=True,
        )
        request = RequestFactory().post(
            '/admin/mediavalet/import/',
            data={
                'file_url': 'https://assets.mediavaletcdn.com/image.png',
                'file_name': 'image.png',
                'title': 'Image',
            },
            content_type='application/json',
        )
        request.user = user

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch('mediavalet.views.requests.get', return_value=Response()):
                    with patch.object(CigionlineImage, 'save', side_effect=Exception('db down')):
                        with self.assertRaises(Exception):
                            import_asset_view(request)

                stored_files = [
                    filename
                    for root, _, files in os.walk(media_root)
                    for filename in files
                ]
                self.assertEqual(stored_files, [])
