from django.template import Context, Template
from django.test import TestCase

from .models import Menu, MenuItem


class MenuTests(TestCase):
    def menu_template(self, slug):
        return Template(
            '{% load menu_tags %}'
            '{% get_menu_items "' + slug + '" as main_menu_items %}'
            '<ul>'
            '{% for menu_item in main_menu_items %}'
            '<li>{{ menu_item.title }}</li>'
            '{% endfor %}'
            '</ul>'
        )

    def test_all_menus_should_be_empty(self):
        about_menu_render = self.menu_template('about').render(Context({}))
        self.assertIn('<ul></ul>', about_menu_render)

        footer_menu_render = self.menu_template('footer').render(Context({}))
        self.assertIn('<ul></ul>', footer_menu_render)

        events_menu_rendered = self.menu_template('events').render(Context({}))
        self.assertIn('<ul></ul>', events_menu_rendered)

        experts_menu_rendered = self.menu_template('experts').render(Context({}))
        self.assertIn('<ul></ul>', experts_menu_rendered)

        main_menu_rendered = self.menu_template('main').render(Context({}))
        self.assertIn('<ul></ul>', main_menu_rendered)

        multimedia_menu_rendered = self.menu_template('multimedia').render(Context({}))
        self.assertIn('<ul></ul>', multimedia_menu_rendered)

        opinions_menu_rendered = self.menu_template('opinions').render(Context({}))
        self.assertIn('<ul></ul>', opinions_menu_rendered)

        publications_menu_rendered = self.menu_template('publications').render(Context({}))
        self.assertIn('<ul></ul>', publications_menu_rendered)

        research_menu_rendered = self.menu_template('research').render(Context({}))
        self.assertIn('<ul></ul>', research_menu_rendered)

    def test_menus_should_have_single_item(self):
        about_menu = Menu.objects.get(slug='about')
        MenuItem.objects.create(title='About Item', menu=about_menu)
        footer_menu = Menu.objects.get(slug='footer')
        MenuItem.objects.create(title='Footer Item', menu=footer_menu)
        events_menu = Menu.objects.get(slug='events')
        MenuItem.objects.create(title='Events Item', menu=events_menu)
        experts_menu = Menu.objects.get(slug='experts')
        MenuItem.objects.create(title='Experts Item', menu=experts_menu)
        main_menu = Menu.objects.get(slug='main')
        MenuItem.objects.create(title='Main Item', menu=main_menu)
        multimedia_menu = Menu.objects.get(slug='multimedia')
        MenuItem.objects.create(title='Multimedia Item', menu=multimedia_menu)
        opinions_menu = Menu.objects.get(slug='opinions')
        MenuItem.objects.create(title='Opinions Item', menu=opinions_menu)
        publications_menu = Menu.objects.get(slug='publications')
        MenuItem.objects.create(title='Publications Item', menu=publications_menu)
        research_menu = Menu.objects.get(slug='research')
        MenuItem.objects.create(title='Research Item', menu=research_menu)

        about_menu_render = self.menu_template('about').render(Context({}))
        self.assertIn('<ul><li>About Item</li></ul>', about_menu_render)

        footer_menu_render = self.menu_template('footer').render(Context({}))
        self.assertIn('<ul><li>Footer Item</li></ul>', footer_menu_render)

        events_menu_rendered = self.menu_template('events').render(Context({}))
        self.assertIn('<ul><li>Events Item</li></ul>', events_menu_rendered)

        experts_menu_rendered = self.menu_template('experts').render(Context({}))
        self.assertIn('<ul><li>Experts Item</li></ul>', experts_menu_rendered)

        main_menu_rendered = self.menu_template('main').render(Context({}))
        self.assertIn('<ul><li>Main Item</li></ul>', main_menu_rendered)

        multimedia_menu_rendered = self.menu_template('multimedia').render(Context({}))
        self.assertIn('<ul><li>Multimedia Item</li></ul>', multimedia_menu_rendered)

        opinions_menu_rendered = self.menu_template('opinions').render(Context({}))
        self.assertIn('<ul><li>Opinions Item</li></ul>', opinions_menu_rendered)

        publications_menu_rendered = self.menu_template('publications').render(Context({}))
        self.assertIn('<ul><li>Publications Item</li></ul>', publications_menu_rendered)

        research_menu_rendered = self.menu_template('research').render(Context({}))
        self.assertIn('<ul><li>Research Item</li></ul>', research_menu_rendered)

    def test_menus_should_have_correct_item_order(self):
        about_menu = Menu.objects.get(slug='about')
        MenuItem.objects.create(title='About Item 1', menu=about_menu, sort_order=1)
        MenuItem.objects.create(title='About Item 2', menu=about_menu, sort_order=0)
        footer_menu = Menu.objects.get(slug='footer')
        MenuItem.objects.create(title='Footer Item 1', menu=footer_menu, sort_order=1)
        MenuItem.objects.create(title='Footer Item 2', menu=footer_menu, sort_order=0)
        events_menu = Menu.objects.get(slug='events')
        MenuItem.objects.create(title='Events Item 1', menu=events_menu, sort_order=1)
        MenuItem.objects.create(title='Events Item 2', menu=events_menu, sort_order=0)
        experts_menu = Menu.objects.get(slug='experts')
        MenuItem.objects.create(title='Experts Item 1', menu=experts_menu, sort_order=1)
        MenuItem.objects.create(title='Experts Item 2', menu=experts_menu, sort_order=0)
        main_menu = Menu.objects.get(slug='main')
        MenuItem.objects.create(title='Main Item 1', menu=main_menu, sort_order=1)
        MenuItem.objects.create(title='Main Item 2', menu=main_menu, sort_order=0)
        multimedia_menu = Menu.objects.get(slug='multimedia')
        MenuItem.objects.create(title='Multimedia Item 1', menu=multimedia_menu, sort_order=1)
        MenuItem.objects.create(title='Multimedia Item 2', menu=multimedia_menu, sort_order=0)
        opinions_menu = Menu.objects.get(slug='opinions')
        MenuItem.objects.create(title='Opinions Item 1', menu=opinions_menu, sort_order=1)
        MenuItem.objects.create(title='Opinions Item 2', menu=opinions_menu, sort_order=0)
        publications_menu = Menu.objects.get(slug='publications')
        MenuItem.objects.create(title='Publications Item 1', menu=publications_menu, sort_order=1)
        MenuItem.objects.create(title='Publications Item 2', menu=publications_menu, sort_order=0)
        research_menu = Menu.objects.get(slug='research')
        MenuItem.objects.create(title='Research Item 1', menu=research_menu, sort_order=1)
        MenuItem.objects.create(title='Research Item 2', menu=research_menu, sort_order=0)

        about_menu_render = self.menu_template('about').render(Context({}))
        self.assertIn('<ul><li>About Item 2</li><li>About Item 1</li></ul>', about_menu_render)

        footer_menu_render = self.menu_template('footer').render(Context({}))
        self.assertIn('<ul><li>Footer Item 2</li><li>Footer Item 1</li></ul>', footer_menu_render)

        events_menu_rendered = self.menu_template('events').render(Context({}))
        self.assertIn('<ul><li>Events Item 2</li><li>Events Item 1</li></ul>', events_menu_rendered)

        experts_menu_rendered = self.menu_template('experts').render(Context({}))
        self.assertIn('<ul><li>Experts Item 2</li><li>Experts Item 1</li></ul>', experts_menu_rendered)

        main_menu_rendered = self.menu_template('main').render(Context({}))
        self.assertIn('<ul><li>Main Item 2</li><li>Main Item 1</li></ul>', main_menu_rendered)

        multimedia_menu_rendered = self.menu_template('multimedia').render(Context({}))
        self.assertIn('<ul><li>Multimedia Item 2</li><li>Multimedia Item 1</li></ul>', multimedia_menu_rendered)

        opinions_menu_rendered = self.menu_template('opinions').render(Context({}))
        self.assertIn('<ul><li>Opinions Item 2</li><li>Opinions Item 1</li></ul>', opinions_menu_rendered)

        publications_menu_rendered = self.menu_template('publications').render(Context({}))
        self.assertIn('<ul><li>Publications Item 2</li><li>Publications Item 1</li></ul>', publications_menu_rendered)

        research_menu_rendered = self.menu_template('research').render(Context({}))
        self.assertIn('<ul><li>Research Item 2</li><li>Research Item 1</li></ul>', research_menu_rendered)
