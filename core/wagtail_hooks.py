from urllib.parse import urlparse

from django import forms
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.exceptions import FieldDoesNotExist
from django.db.models import F
from django.shortcuts import render
from django.urls import path, reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.admin import messages
from wagtail.admin.auth import permission_required
from wagtail.admin.menu import MenuItem
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler,
    InlineStyleElementHandler,
)
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.contrib.frontend_cache.utils import purge_urls_from_cache
from wagtail import hooks
from wagtail.models import Page, Site
from .models import Theme, QRCodeScan, QRCodeDocumentScan
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions


PURGE_PAGE_TYPE_OPTIONS = {
    'articles.ArticlePage': {
        'label': 'Opinions',
        'type_field': 'article_type',
        'form_field': 'article_types',
    },
    'publications.PublicationPage': {
        'label': 'Publications',
        'type_field': 'publication_type',
        'form_field': 'publication_types',
    },
    'multimedia.MultimediaPage': {
        'label': 'Multimedia',
        'type_field': 'multimedia_type',
        'form_field': 'multimedia_types',
    },
    'articles.ArticleSeriesPage': {
        'label': 'Essay series',
    },
    'multimedia.MultimediaSeriesPage': {
        'label': 'Multimedia series',
    },
    'core.BasicPage': {
        'label': 'Basic pages',
    },
}

TEMPLATE_FRAGMENT_CACHE_OPTIONS = {
    'footer': 'Footer',
    'top_bar': 'Top bar',
}

TEMPLATE_FRAGMENT_CACHE_NAMES = {
    'footer': ['footer', 'footer_homepage'],
    'top_bar': ['top_bar'],
}


class PurgeCloudflareCacheForm(forms.Form):
    pages = forms.CharField(
        label='Pages to purge',
        help_text='Enter one page URL, path, or Wagtail page ID per line.',
        widget=forms.Textarea(attrs={'rows': 12}),
        required=False,
    )
    page_types = forms.MultipleChoiceField(
        label='Page types',
        choices=[(value, option['label']) for value, option in PURGE_PAGE_TYPE_OPTIONS.items()],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    themes = forms.ModelMultipleChoiceField(
        label='Themes',
        queryset=Theme.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    article_types = forms.ModelMultipleChoiceField(
        label='Article types',
        queryset=apps.get_model('articles', 'ArticleTypePage').objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    publication_types = forms.ModelMultipleChoiceField(
        label='Publication types',
        queryset=apps.get_model('publications', 'PublicationTypePage').objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    multimedia_types = forms.MultipleChoiceField(
        label='Multimedia types',
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MultimediaPage = apps.get_model('multimedia', 'MultimediaPage')
        self.fields['themes'].queryset = Theme.objects.order_by('name')
        self.fields['article_types'].queryset = apps.get_model('articles', 'ArticleTypePage').objects.live().order_by('title')
        self.fields['publication_types'].queryset = apps.get_model('publications', 'PublicationTypePage').objects.live().order_by('title')
        self.fields['multimedia_types'].choices = MultimediaPage._meta.get_field('multimedia_type').choices

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('pages') and not cleaned_data.get('page_types'):
            raise forms.ValidationError('Enter page URLs/IDs or choose at least one page type.')
        return cleaned_data


def get_purge_cache_url(item):
    item = item.strip()
    if not item:
        return None

    if item.isdigit():
        try:
            return Page.objects.live().get(pk=item).get_full_url()
        except Page.DoesNotExist:
            raise forms.ValidationError(f'No live Wagtail page found with ID {item}.')

    parsed = urlparse(item)
    if parsed.scheme and parsed.netloc:
        return item

    if item.startswith('/'):
        return Site.objects.get(is_default_site=True).root_url + item

    raise forms.ValidationError(f'Enter a full URL, path starting with /, or page ID: {item}')


def get_filter_purge_cache_urls(cleaned_data):
    urls, _debug_rows = get_filter_purge_cache_urls_debug(cleaned_data)
    return urls


def debug_sql(queryset):
    sql, params = queryset.query.sql_with_params()
    return f'{sql}\n\nparams: {params}'


def model_has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
    except FieldDoesNotExist:
        return False
    return True


def get_page_purge_url(page, site=None):
    url = page.get_full_url()
    if url:
        return url

    site = site or Site.objects.get(is_default_site=True)
    root_path = site.root_page.url_path

    if page.url_path.startswith(root_path):
        path = '/' + page.url_path[len(root_path):]
    else:
        path = page.url_path

    return site.root_url + path


def get_filter_purge_cache_urls_debug(cleaned_data):
    urls = []
    debug_rows = []
    default_site = Site.objects.get(is_default_site=True)

    for page_type in cleaned_data.get('page_types'):
        options = PURGE_PAGE_TYPE_OPTIONS[page_type]
        model = apps.get_model(page_type)
        raw_queryset = model.objects.all()
        live_queryset = raw_queryset.live()
        public_queryset = live_queryset.public()
        queryset = live_queryset
        row = {
            'page_type': options['label'],
            'model': page_type,
            'filters': [],
            'raw_count': raw_queryset.count(),
            'live_count': live_queryset.count(),
            'public_count': public_queryset.count(),
            'base_sql': debug_sql(queryset),
        }

        if cleaned_data.get('themes') and model_has_field(model, 'theme'):
            themes = list(cleaned_data['themes'])
            queryset = queryset.filter(theme__in=cleaned_data['themes'])
            row['filters'].append({
                'label': 'Themes',
                'values': [theme.name for theme in themes],
                'count': queryset.count(),
                'sql': debug_sql(queryset),
            })

        form_field = options.get('form_field')
        type_field = options.get('type_field')
        if form_field and cleaned_data.get(form_field):
            values = list(cleaned_data[form_field])
            queryset = queryset.filter(**{f'{type_field}__in': cleaned_data[form_field]})
            row['filters'].append({
                'label': model._meta.get_field(type_field).verbose_name.title(),
                'values': [str(value) for value in values],
                'count': queryset.count(),
                'sql': debug_sql(queryset),
            })

        pages = list(queryset)
        page_urls = [get_page_purge_url(page, default_site) for page in pages]
        page_debug = [
            {
                'title': page.title,
                'url_path': page.url_path,
                'full_url': page.get_full_url(),
                'purge_url': url,
            }
            for page, url in zip(pages, page_urls)
        ]
        row['matched_count'] = len(pages)
        row['url_count'] = len(page_urls)
        row['urls'] = page_urls
        row['pages'] = page_debug
        row['final_sql'] = debug_sql(queryset)
        debug_rows.append(row)
        urls.extend(page_urls)

    return urls, debug_rows


def clear_template_fragment_cache(fragment_name):
    if fragment_name not in TEMPLATE_FRAGMENT_CACHE_OPTIONS:
        raise forms.ValidationError('Choose a valid template fragment cache to clear.')

    for cache_name in TEMPLATE_FRAGMENT_CACHE_NAMES[fragment_name]:
        cache.delete(make_template_fragment_key(cache_name))


def render_purge_cloudflare_cache(request, context):
    context['template_fragment_cache_options'] = TEMPLATE_FRAGMENT_CACHE_OPTIONS
    return render(request, 'core/admin/purge_cloudflare_cache.html', context)


@permission_required('wagtailadmin.access_admin')
def purge_cloudflare_cache_view(request):
    if request.method == 'POST':
        fragment_name = request.POST.get('template_fragment')
        if fragment_name:
            try:
                clear_template_fragment_cache(fragment_name)
            except forms.ValidationError as error:
                for message in error.messages:
                    messages.error(request, message)
            else:
                messages.success(
                    request,
                    f'Cleared the {TEMPLATE_FRAGMENT_CACHE_OPTIONS[fragment_name]} template fragment cache.',
                )

            return render_purge_cloudflare_cache(
                request,
                {
                    'form': PurgeCloudflareCacheForm(),
                },
            )

        form = PurgeCloudflareCacheForm(request.POST)
        if form.is_valid():
            urls = []
            errors = []
            for item in form.cleaned_data['pages'].splitlines():
                try:
                    url = get_purge_cache_url(item)
                except forms.ValidationError as error:
                    errors.extend(error.messages)
                else:
                    if url:
                        urls.append(url)

            filter_urls, debug_rows = get_filter_purge_cache_urls_debug(form.cleaned_data)
            urls.extend(filter_urls)
            urls = list(dict.fromkeys(urls))
            is_preview = 'preview' in request.POST

            if errors:
                for error in errors:
                    messages.error(request, error)
                return render_purge_cloudflare_cache(
                    request,
                    {
                        'form': form,
                        'debug_rows': debug_rows,
                        'preview_urls': urls,
                    },
                )
            elif not urls:
                if form.cleaned_data.get('page_types'):
                    messages.error(request, 'No live public pages matched those filters.')
                else:
                    messages.error(request, 'Enter at least one page to purge.')
                return render_purge_cloudflare_cache(
                    request,
                    {
                        'form': form,
                        'debug_rows': debug_rows,
                    },
                )
            elif is_preview:
                messages.info(request, f'Preview found {len(urls)} URL{"s" if len(urls) != 1 else ""}. Nothing was purged.')
                return render_purge_cloudflare_cache(
                    request,
                    {
                        'form': form,
                        'debug_rows': debug_rows,
                        'preview_urls': urls,
                    },
                )
            elif not getattr(settings, 'WAGTAILFRONTENDCACHE', None):
                messages.error(request, 'No WAGTAILFRONTENDCACHE backend is configured.')
                return render_purge_cloudflare_cache(
                    request,
                    {
                        'form': form,
                        'debug_rows': debug_rows,
                        'preview_urls': urls,
                    },
                )
            else:
                purge_urls_from_cache(urls)
                messages.success(
                    request,
                    f'Purged {len(urls)} URL{"s" if len(urls) != 1 else ""} from Cloudflare.',
                )
                return render_purge_cloudflare_cache(
                    request,
                    {
                        'form': form,
                        'debug_rows': debug_rows,
                        'purged_urls': urls,
                    },
                )
    else:
        form = PurgeCloudflareCacheForm()

    return render_purge_cloudflare_cache(
        request,
        {
            'form': form,
        },
    )


@hooks.register('register_admin_urls')
def register_purge_cloudflare_cache_url():
    return [
        path(
            'purge-cloudflare-cache/',
            purge_cloudflare_cache_view,
            name='purge_cloudflare_cache',
        ),
    ]


@hooks.register('register_settings_menu_item')
def register_purge_cloudflare_cache_menu_item():
    return MenuItem(
        'Purge Cloudflare Cache',
        reverse('purge_cloudflare_cache'),
        icon_name='rotate',
        order=10000,
    )


@hooks.register('construct_page_chooser_queryset')
def sort_event_page_chooser_queryset(queryset, request):
    page_types = {
        page_type.strip().lower()
        for page_type in (request.GET.get('page_type') or '').split(',')
        if page_type.strip()
    }

    if 'events.eventpage' in page_types:
        return queryset.order_by(
            F('contentpage__publishing_date').desc(nulls_last=True),
            '-latest_revision_created_at',
            '-id',
        )

    return queryset


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static('css/admin.css'))


@hooks.register('insert_editor_js')
def editor_js():
    return mark_safe(
        """
        <script>
            /**
            * @param {jQuery} $
            */
            window.addEventListener("DOMContentLoaded", (event) => {
                var times = [];
                for (let i = 0; i < 24; i++) {
                    var hour = i < 10 ? "0" + i : i;
                    times.push(hour + ":" + "00");
                    times.push(hour + ":" + "30");
                }
                $("#id_go_live_at").siblings("script").innerHtml = initDateTimeChooser(
                    "id_go_live_at",
                    {"dayOfWeekStart": 0, "format": "Y-m-d H:i", "formatTime": "H:i", "allowTimes": times}
                );
                $("#id_go_live_at").attr("readonly", "")
            });
        </script>
        """
    )


@hooks.register('register_rich_text_features')
def register_rich_text_drop_cap(features):
    feature_name = 'dropcap'
    type_ = 'DROPCAP'

    control = {
        'type': type_,
        'icon': 'title',
        'description': 'Drop cap',
        'element': 'div',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'div[class=drop-caps]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'div', 'props': {'class': 'drop-caps'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_name(features):
    feature_name = 'name'
    type_ = 'NAME'

    control = {
        'type': type_,
        'label': 'Name',
        'description': 'Name',
        'element': 'span',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[class=name]': InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: {'element': 'span', 'props': {'class': 'name'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_coloured(features):
    feature_name = 'coloured'
    type_ = 'COLOURED'

    control = {
        'type': type_,
        'label': 'Coloured',
        'description': 'Coloured',
        'element': 'span',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[class=coloured]': InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: {'element': 'span', 'props': {'class': 'coloured'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_underline(features):
    feature_name = 'underline'
    type_ = 'UNDERLINE'

    control = {
        'type': type_,
        'label': 'U',
        'description': 'underline',
        'element': 'span',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[class=underline]': InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: {'element': 'span', 'props': {'class': 'underline'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_paragraph_heading(features):
    feature_name = 'paragraph_heading'
    type_ = 'HEADING'

    control = {
        'type': type_,
        'label': 'Heading',
        'description': 'Paragraph Heading',
        'element': 'h2',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'h2[class=paragraph-heading]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'h2', 'props': {'class': 'paragraph-heading'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_rtl(features):
    feature_name = 'rtl'
    type_ = 'RTL'

    control = {
        'type': type_,
        'label': 'R',
        'description': 'Right-to-left language support',
        'element': 'p',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'p[dir=rtl]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'p', 'props': {'dir': 'rtl'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_source(features):
    feature_name = 'source'
    type_ = 'SOURCE'

    control = {
        'type': type_,
        'label': 'Source',
        'description': 'Source',
        'element': 'p',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'p[class=hover-reveal-quote-source]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'p', 'props': {'class': 'hover-reveal-quote-source'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_red_line(features):
    feature_name = 'red-line'
    type_ = 'REDLINE'

    control = {
        'type': type_,
        'label': 'Red Line',
        'description': 'Red Line',
        'element': 'div',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'div[class=cigi-red-line]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'div', 'props': {'class': 'cigi-red-line'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_chair_name(features):
    feature_name = 'chair-name'
    type_ = 'CHAIRNAME'

    control = {
        'type': type_,
        'label': 'Chair Name',
        'description': 'Chair Name',
        'element': 'p',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'p[class=chair-name]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'p', 'props': {'class': 'chair-name'}}}},
    })


class AboutListingViewSet(ModelViewSet):
    model = Page
    menu_label = 'About'
    menu_icon = 'help'
    menu_order = 110
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('title',)
    form_fields = ['title']
    page_names = [
        'CIGI History',
        'Our Partners',
        'CIGI Campus',
        'Strategy and Evaluation',
        'The CIGI Rule',
    ]
    add_to_admin_menu = True

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs["queryset"] = self.model.objects.filter(title__in=AboutListingViewSet.page_names)
        return kwargs


class ThemeListingViewSet(ModelViewSet):
    model = Theme
    menu_label = 'Themes'
    icon = 'image'
    menu_icon = 'image'
    menu_order = 204
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('name',)
    ordering = ['name']
    add_to_admin_menu = True
    exclude_form_fields = []


@hooks.register("register_admin_viewset")
def register_theme_viewset():
    return ThemeListingViewSet()


@hooks.register("register_admin_viewset")
def register_about_viewset():
    return AboutListingViewSet()


def qr_page_title_link(obj):
    return format_html(
        '<a href="/admin/pages/{}/edit/">{}</a>',
        obj.page_id,
        obj.page.title,
    )


def qr_document_title_link(obj):
    return format_html(
        '<a href="/admin/documents/{}/edit/">{}</a>',
        obj.document_id,
        obj.document.title,
    )


class QRCodePageScanViewSet(ModelViewSet):
    model = QRCodeScan
    menu_label = 'Page QR Scans'
    menu_icon = 'link'
    name = 'qrcodescan'
    exclude_form_fields = []
    list_display = [
        Column(qr_page_title_link, label='Page'),
        Column('scan_count', label='Scan Count', sort_key='scan_count'),
        Column('last_scanned', label='Last Scanned', sort_key='last_scanned'),
    ]
    ordering = ['-scan_count']

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs['queryset'] = QRCodeScan.objects.select_related('page').all()
        return kwargs


class QRCodeDocumentScanViewSet(ModelViewSet):
    model = QRCodeDocumentScan
    menu_label = 'Document QR Scans'
    menu_icon = 'doc-full'
    name = 'qrcodedocumentscan'
    exclude_form_fields = []
    list_display = [
        Column(qr_document_title_link, label='Document'),
        Column('scan_count', label='Scan Count', sort_key='scan_count'),
        Column('last_scanned', label='Last Scanned', sort_key='last_scanned'),
    ]
    ordering = ['-scan_count']

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs['queryset'] = QRCodeDocumentScan.objects.select_related('document').all()
        return kwargs


class QRCodeViewSetGroup(ViewSetGroup):
    menu_label = 'QR Codes'
    menu_icon = 'link'
    menu_order = 250
    items = (
        QRCodePageScanViewSet,
        QRCodeDocumentScanViewSet,
    )


@hooks.register('register_admin_viewset')
def register_qr_code_viewsets():
    return QRCodeViewSetGroup()
