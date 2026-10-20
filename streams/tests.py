from types import SimpleNamespace

from django.test import SimpleTestCase
from django.template.loader import render_to_string
from wagtail import blocks

from streams.blocks import AutoPlayVideoBlock, ButtonBlock


class AutoPlayVideoBlockTests(SimpleTestCase):
    def test_uses_dph_page_template(self):
        page = SimpleNamespace(
            _meta=SimpleNamespace(verbose_name='Page'),
            theme=SimpleNamespace(name='DPH'),
        )

        template = AutoPlayVideoBlock().get_template({}, {'page': page})

        self.assertEqual(template, 'themes/dph/streams/page_autoplay_video_block.html')

    def test_dph_page_template_has_no_grid_wrappers(self):
        html = render_to_string(
            'themes/dph/streams/page_autoplay_video_block.html',
            {'self': SimpleNamespace(
                video=SimpleNamespace(url='/media/video.mp4'),
                caption='Video caption',
                disable_autoplay=False,
            )},
        )

        self.assertNotIn('class="container"', html)
        self.assertNotIn('class="row', html)
        self.assertNotIn('class="col', html)
        self.assertIn('<video playsinline autoplay muted controls>', html)

    def test_autoplay_can_be_disabled(self):
        for template in (
            'streams/autoplay_video_block.html',
            'themes/dph/streams/page_autoplay_video_block.html',
        ):
            with self.subTest(template=template):
                html = render_to_string(template, {'self': SimpleNamespace(
                    video=SimpleNamespace(url='/media/video.mp4'),
                    caption='',
                    disable_autoplay=True,
                )})

                self.assertIn('<video playsinline muted controls>', html)


class ButtonBlockTests(SimpleTestCase):
    def test_requires_page_or_url(self):
        with self.assertRaises(blocks.StructBlockValidationError):
            ButtonBlock().clean({
                'text': 'Read more',
                'page': None,
                'url': '',
            })
