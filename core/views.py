import logging

import requests
from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from core.emailing import (
    send_facility_rental_confirmation_email,
    send_facility_rental_email,
    send_general_inquiry_confirmation_email,
    send_general_inquiry_email,
)
from core.forms import FacilityRentalInquiryForm, GeneralInquiryForm
from core.models import ContentPage, QRCodeScan, QRCodeDocumentScan
from core.models_settings import EmailFormSettings
from datetime import date
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode, urlparse, urlunparse
from wagtail.models import Page

logger = logging.getLogger(__name__)


@never_cache
def qr_redirect(request, page_id):
    page = get_object_or_404(Page, id=page_id, live=True)
    scan, _ = QRCodeScan.objects.get_or_create(page=page)
    QRCodeScan.objects.filter(pk=scan.pk).update(
        scan_count=F('scan_count') + 1,
        last_scanned=timezone.now(),
    )
    base_url = page.specific.full_url
    utm_params = urlencode({
        'utm_source': 'qr_code',
        'utm_medium': 'qr',
        'utm_campaign': 'qr_scan',
    })
    parsed = urlparse(base_url)
    # Preserve any existing query params on the destination URL
    existing_qs = parsed.query
    full_qs = f'{existing_qs}&{utm_params}' if existing_qs else utm_params
    destination = urlunparse(parsed._replace(query=full_qs))
    return redirect(destination)


@never_cache
def qr_document_redirect(request, doc_id):
    from wagtail.documents.models import Document
    doc = get_object_or_404(Document, id=doc_id)
    scan, _ = QRCodeDocumentScan.objects.get_or_create(document=doc)
    QRCodeDocumentScan.objects.filter(pk=scan.pk).update(
        scan_count=F('scan_count') + 1,
        last_scanned=timezone.now(),
    )
    return redirect(doc.url)


def ar_timeline_pages(request):
    if request.user.is_authenticated:
        year = int(request.GET.get('year')) if request.GET.get('year') else date.today().year
        content_pages = ContentPage.objects.live().filter(projectpage=None, publicationseriespage=None, multimediaseriespage=None, twentiethpagesingleton=None, multimediapage=None, articleseriespage=None).exclude(articlepage__article_type__title__in=['CIGI in the News', 'News Releases', 'Op-Eds']).filter(publishing_date__range=[f'{year - 1}-08-01', f'{year}-07-31'])

        json_items = []

        for content_page in content_pages:
            type = ''
            subtype = []
            authors = ''
            speakers = ''
            event_date = ''
            summary = ''
            subtitle = content_page.specific.subtitle
            publishing_date = ''
            image = ''
            if content_page.contenttype == 'Event':
                type = 'event'
                speakers = content_page.author_names
                event_date = content_page.publishing_date
                image = content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else ''
            else:
                authors = content_page.author_names
                publishing_date = content_page.publishing_date

            if content_page.contenttype == 'Opinion':
                type = 'article'
                subtype = [content_page.contentsubtype] if content_page.contentsubtype else []
                image = content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else ''
            if content_page.contenttype == 'Publication':
                type = 'publication'
                subtype = [content_page.contentsubtype] if content_page.contentsubtype else []
                image = content_page.specific.image_feature.get_rendition('fill-1600x900').url if content_page.specific.image_feature else ''
            try:
                summary = content_page.specific.short_description
            except AttributeError:
                summary = ''
                if content_page.specific.subtitle:
                    summary = content_page.specific.subtitle
                else:
                    for block in content_page.specific.body:
                        if block.block_type == 'paragraph':
                            summary += str(block.value)

            json_items.append({
                'id': str(content_page.id),
                'title': content_page.title,
                'subtitle': subtitle,
                'authors': authors if authors else [],
                'speakers': speakers if speakers else [],
                'published_date': publishing_date,
                'event_date': event_date,
                'url_landing_page': content_page.url,
                'pdf_url': content_page.pdf_download,
                'type': type,
                'subtype': subtype,
                'word_count': content_page.specific.word_count,
                'summary': summary,
                'image': image,
            })

        return JsonResponse({
            'meta': {
                'total_count': content_pages.count(),
            },
            'items': json_items
        })
    return HttpResponse('Unauthorized', status=401)


def old_images(request):
    if request.user.is_authenticated:
        content_pages = ContentPage.objects.filter(articlepage__isnull=False).filter(publishing_date__lt='2017-01-01')
        pages = []
        for content_page in content_pages:
            if content_page.specific.image_hero:
                pages.append({
                    'id': content_page.id,
                    'url': content_page.url,
                    'title': content_page.title,
                    'publishing_date': content_page.publishing_date,
                    'image_hero_url_1600_900': content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else '',
                    'image_hero_url_width_1760': content_page.specific.image_hero.get_rendition('width-1760').url if content_page.specific.image_hero else '',
                    'image_feature_url': content_page.specific.image_feature.get_rendition('fill-1600x900').url if content_page.specific.image_feature else '',
                })
        pages.sort(key=lambda x: x['publishing_date'], reverse=True)
        return TemplateResponse(request, 'core/old_pages_list.html', {'pages': pages, 'count': len(pages)})
    return HttpResponse('Unauthorized', status=401)


def years(request):
    years = ContentPage.objects.filter(publishing_date__year__isnull=False).values_list('publishing_date__year', flat=True).distinct().order_by('-publishing_date__year')
    return JsonResponse({
        'years': list(years)
    })


def oauth_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')  # original URL

    token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    payload = {
        'grant_type': 'authorization_code',
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.AUTH0_REDIRECT_URI,
    }

    res = requests.post(token_url, json=payload)
    if res.status_code == 200:
        token_data = res.json()
        access_token = token_data.get('access_token')
        request.session['auth0_access_token'] = access_token
    else:
        # Log or handle error
        pass

    return redirect(state or '/')


# =============================================================================
# Design-system test-page index  (dev/QA tool — served at /ds-test-pages/)
# -----------------------------------------------------------------------------
# Single source of truth for the throwaway block test pages. Entries are
# (label, slug); the view resolves each slug to its live URL at request time,
# so this list is the only thing to maintain.
#
# BUILD-LOOP STEP: after a new block's test page passes in-browser validation,
# append its (label, slug) here. The index at /ds-test-pages/ updates itself.
# See docs/redesign/test-pages.md.
# =============================================================================
DS_TEST_PAGES = [
    ('Modules', [
        ('Primary Hero', 'primary-hero-test'),
        ('Alt Hero (block)', 'alt-hero'),
        ('Branded / Split Hero (block)', 'branded-hero-test'),
        ('CTA', 'cta-image'),
        ('Banner', 'banner-test'),
        ('Image + Content — image left', 'image-text-left'),
        ('Image + Content — image right', 'image-text-right'),
        ('Stats — light', 'stats-light'),
        ('Stats — dark', 'stats-dark'),
        ('Stats — green', 'stats-green'),
        ('Text', 'text-columns'),
        ('Accordion', 'accordion-module-figma-check'),
        ('Horizontal Tabs', 'horizontal-tabs-test'),
        ('Text Card Grid', 'text-card-grid-test'),
        ('Full Width Media / Video + Text', 'video-text'),
        ('Form — multi-step', 'form-test'),
        ('Newsletter signup', 'newsletter-test'),
        ('Program Spotlight (dynamic)', 'program-spotlight-test'),
        ('Program Grid (dynamic)', 'program-grid-test'),
        ('Experts Grid (dynamic, paginated)', 'experts-grid-test'),
    ]),
    ('Carousels', [
        ('Gallery', 'gallery-text'),
        ('Gallery — with button', 'gallery-text-button'),
        ('Supporting Materials', 'supporting-materials'),
        ('Video Carousel', 'video-carousel-test'),
        ('Programs Carousel (dynamic, light + dark)', 'programs-carousel-test'),
        ('Experts Carousel (dynamic)', 'experts-carousel-test'),
        ('Resource Carousel (dynamic)', 'resource-carousel-test'),
        ('Events Carousel (dynamic)', 'events-carousel-test'),
    ]),
    ('Dynamic — other', [
        ('Resource Bento (dynamic)', 'resource-bento-test'),
        ('Trending Issues banner (dynamic)', 'trending-issues-test'),
        ('Jobs List (dynamic)', 'jobs-list-test'),
        ('News Grid — In the News (dynamic)', 'news-grid-test'),
    ]),
    ('Composable tabs + faceted listing', [
        # The composable Tabs block + the faceted-listing module (every card type,
        # the no-filter grid, A–Z facet, lazy panels) in one isolated surface.
        ('Composable Tabs + Faceted Listing (all card types)', 'composable-tabs-test'),
        # Standalone faceted-listing (no tabs): episode_row card, single-select
        # Season facet, single-column row grid — the Podcast All-Episodes module.
        ('Podcast All-Episodes (episode_row + Season facet)', 'podcast-all-episodes-test'),
        # News archive: news card, prefiltered to a type (CIGI News), restricted
        # TYPE facet {CIGI News, CIGI in the News, Opinion-Eds} only.
        ('CIGI News archive (news + restricted TYPE facet)', 'news-router-test'),
    ]),
]


def ds_test_pages(request):
    """Dev/QA index linking every design-system block test page."""
    groups = []
    for group_name, entries in DS_TEST_PAGES:
        items = []
        for label, slug in entries:
            page = Page.objects.filter(slug=slug, live=True).first()
            # Host-relative path (not page.url, which uses the site's configured
            # hostname) so links work on localhost / staging / prod alike.
            items.append({
                'label': label,
                'slug': slug,
                'url': urlparse(page.url).path if page else None,
            })
        groups.append({'name': group_name, 'items': items})
    # Component previews are plain views (not Wagtail pages) — appended with a
    # direct URL so they show in the same index.
    groups.append({'name': 'Components', 'items': [
        {'label': 'Card variants', 'url': reverse('ds_cards_preview'), 'slug': None},
        {'label': 'CPT heroes', 'url': reverse('ds_heroes_preview'), 'slug': None},
    ]})
    return TemplateResponse(request, 'ds_test_pages.html', {'groups': groups})


def ds_cards_preview(request):
    """Dev/QA preview of the shared card variants rendered from real pages.

    Not a Wagtail page — a plain view so card variants can be eyeballed before
    a consuming dynamic module exists. Served at /ds-test-pages/cards/.
    """
    from research.models import ThemeProgram

    media_cards = []
    for row in ThemeProgram.objects.select_related('program', 'theme')[:6]:
        program = row.program
        if not program.live or program.archive == 1:
            continue
        media_cards.append({
            'page': program,
            'accent_class': row.theme.accent_surface_class,
        })

    # Prefer content with a project (so pills render); take specific so the
    # template can show feature images on the variants that have them.
    list_pages = (ContentPage.objects.live().public()
                  .filter(projects__isnull=False).distinct()
                  .order_by('-publishing_date').specific()[:6])

    from events.models import EventPage
    event_pages = (EventPage.objects.live().public()
                   .order_by('-publishing_date')[:3])

    # An expert with every slot populated, so the toggle combinations are visible.
    from people.models import PersonPage
    expert = (PersonPage.objects.live().public()
              .filter(image_square__isnull=False, short_bio__isnull=False,
                      derived_topics__isnull=False,
                      content_pages_as_author__isnull=False)
              .exclude(short_bio='').distinct().first())

    share_demo_links = [
        {'platform': 'x', 'url': 'https://x.com/cigionline'},
        {'platform': 'linkedin', 'url': 'https://www.linkedin.com/company/cigi'},
        {'platform': 'instagram', 'url': 'https://www.instagram.com/cigionline'},
        {'platform': 'youtube', 'url': 'https://www.youtube.com/user/cigivideos'},
        {'platform': 'spotify', 'url': 'https://open.spotify.com/'},
        {'platform': 'apple-podcasts', 'url': 'https://podcasts.apple.com/'},
    ]

    return TemplateResponse(request, 'ds_card_preview.html', {
        'media_cards': media_cards,
        'list_pages': list_pages,
        'event_pages': event_pages,
        'expert': expert,
        'share_demo_links': share_demo_links,
    })


def ds_heroes_preview(request):
    """Dev/QA preview of the CPT heroes (core.heroes) rendered from real pages.

    Staged here so the page-model-specific heroes can be reviewed before they're
    wired into the live page templates. Served at /ds-test-pages/heroes/.
    """
    from core.heroes import (article_hero_data, publication_hero_data,
                             event_hero_data, person_hero_data, podcast_hero_data)
    from publications.models import PublicationPage
    from events.models import EventPage
    from people.models import PersonPage
    from multimedia.models import MultimediaPage

    def first(qs):
        return qs.live().public().exclude(slug__contains='-test').first()

    article = (ContentPage.objects.live().public()
               .filter(topics__isnull=False).distinct()
               .exclude(slug__contains='-test')
               .order_by('-publishing_date').specific().first())
    publication = first(PublicationPage.objects)
    event = first(EventPage.objects)
    multimedia = first(MultimediaPage.objects)
    person = (PersonPage.objects.live().public()
              .filter(person_types=4, image_square__isnull=False).first())

    heroes = []
    if article:
        heroes.append({'label': 'Article / Opinion Hero', 'hero': article_hero_data(article)})
        heroes.append({'label': 'Simple Article Hero', 'hero': article_hero_data(article, simple=True)})
    if publication:
        heroes.append({'label': 'Publication Hero', 'hero': publication_hero_data(publication)})
        heroes.append({'label': 'Simple Publication Hero', 'hero': publication_hero_data(publication, simple=True)})
    if event:
        heroes.append({'label': 'Event Hero', 'hero': event_hero_data(event)})
    if person:
        heroes.append({'label': 'Expert Bio Hero', 'hero': person_hero_data(person)})
        heroes.append({'label': 'Simple Expert Bio Hero', 'hero': person_hero_data(person, simple=True)})
    if multimedia:
        heroes.append({'label': 'Podcast / Multimedia Hero', 'hero': podcast_hero_data(multimedia)})

    return TemplateResponse(request, 'ds_heroes_preview.html', {'heroes': heroes})


@never_cache
@ensure_csrf_cookie
@require_GET
def csrf_token(request):
    """Mint the csrftoken cookie on demand (204). DS forms in cached fragments
    rewrite their baked-in token from this cookie (multistep-form.js); minting
    here instead of on every request keeps Set-Cookie/Vary: Cookie off the
    rest of the site so CDN full-page caching survives. See forms.md.

    never_cache is load-bearing: production decorates ALL urlpatterns with
    cache_control(max_age=…) (urls.py) — a cacheable mint would let a shared
    cache hand one visitor's csrftoken to everyone (patch_cache_control keeps
    the min max-age, so this wins)."""
    return HttpResponse(status=204)


def _form_success(request, thanks_page, message, next_url):
    """Post-submit destination for the inquiry forms (BugHerd #355): redirect
    to the configured live thank-you page; without one, back to the hosting
    page with a success message (the original flow)."""
    if thanks_page and thanks_page.live:
        return redirect(thanks_page.get_url(request))
    messages.success(request, message)
    return redirect(next_url)


def venue_rental_inquiry(request):
    """POST target for the Venue Rental form module (FormSectionBlock →
    includes/venue_rental_form.html). Mirrors FacilityRentalsPage.serve: emails
    EmailFormSettings.recipients + a confirmation to the submitter, then
    redirects back to the hosting page (`next`) with a success message. On
    validation errors the bound form re-renders on a standalone page so input
    is preserved.
    """
    if request.method != 'POST':
        return redirect('/')

    next_url = request.POST.get('next') or '/'
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/'

    form = FacilityRentalInquiryForm(request.POST)
    if form.is_valid():
        email_settings = EmailFormSettings.for_request(request)
        if not email_settings.recipients:
            form.add_error(None, 'No recipients are configured. Please contact the site administrator.')
        else:
            try:
                send_facility_rental_email(request, email_settings.recipients, form.cleaned_data)
                send_facility_rental_confirmation_email(form.cleaned_data)
            except Exception:
                logger.exception('Error sending venue rental inquiry email')
                form.add_error(None, 'There was an error sending your request. Please try again later.')
            else:
                # A configured thank-you page wins (BugHerd #355); without one,
                # the old back-to-page flow with a success message remains.
                return _form_success(request, email_settings.venue_thanks_page,
                                     'Thanks! Your facility rental inquiry has been sent.',
                                     next_url)

    return render(request, 'core/venue_rental_form_page.html', {
        'form': form,
        'next_url': next_url,
    })


def general_inquiry(request):
    """POST target for the General Inquiries form module (GeneralInquiryBlock,
    BugHerd #163). Same flow as venue_rental_inquiry: emails
    EmailFormSettings.general_recipients + a confirmation to the submitter,
    then redirects back to the hosting page (`next`) with a success message.
    On validation errors the bound form re-renders on a standalone page so
    input is preserved.
    """
    if request.method != 'POST':
        return redirect('/')

    next_url = request.POST.get('next') or '/'
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/'

    form = GeneralInquiryForm(request.POST)
    if form.is_valid():
        email_settings = EmailFormSettings.for_request(request)
        if not email_settings.general_recipients:
            form.add_error(None, 'No recipients are configured. Please contact the site administrator.')
        else:
            try:
                send_general_inquiry_email(email_settings.general_recipients, form.cleaned_data)
                send_general_inquiry_confirmation_email(form.cleaned_data)
            except Exception:
                logger.exception('Error sending general inquiry email')
                form.add_error(None, 'There was an error sending your request. Please try again later.')
            else:
                return _form_success(request, email_settings.general_thanks_page,
                                     'Thanks! Your message has been sent.',
                                     next_url)

    return render(request, 'core/general_inquiry_form_page.html', {
        'form': form,
        'next_url': next_url,
    })
