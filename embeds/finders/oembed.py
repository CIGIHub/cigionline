import re

from bs4 import BeautifulSoup
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from wagtail.embeds.exceptions import EmbedNotFoundException
from wagtail.embeds.finders.base import EmbedFinder
from wagtail.embeds.finders.oembed import OEmbedFinder
from wagtail.embeds.oembed_providers import youtube

ISSUU_URL_PATTERN = re.compile(r'^https?://(?:www\.)?issuu\.com/([^#?/]+)/docs/([^#?/]+)', re.IGNORECASE)


class IssuuEmbedFinder(EmbedFinder):
    def accept(self, url):
        return bool(ISSUU_URL_PATTERN.match(url))

    def find_embed(self, url, max_width=None, max_height=None):
        match = ISSUU_URL_PATTERN.match(url)
        if not match:
            raise EmbedNotFoundException

        username = match.group(1)
        docname = match.group(2)
        embed_url = 'https://e.issuu.com/embed.html?u={}&d={}'.format(username, docname)
        width = max_width or 760
        html = (
            '<div style="position:relative;padding-top:max(60%,326px);height:0;width:100%">'
            '<iframe'
            ' allow="clipboard-write"'
            ' sandbox="allow-top-navigation allow-top-navigation-by-user-activation'
            ' allow-downloads allow-scripts allow-same-origin allow-popups'
                ' allow-modals allow-popups-to-escape-sandbox allow-forms"'
                ' allowfullscreen="true"'
            ' style="position:absolute;border:none;width:100%;height:100%;left:0;right:0;top:0;bottom:0;"'
            ' src="{}">'
            '</iframe></div>'
        ).format(embed_url)

        return {
            'title': '',
            'author_name': '',
            'provider_name': 'Issuu',
            'type': 'rich',
            'thumbnail_url': None,
            'width': width,
            'height': None,
            'html': html,
        }

class YouTubeOEmbedFinder(OEmbedFinder):
    def __init__(self, providers=None, options=None):
        if providers is None:
            providers = [youtube]

        if providers != [youtube]:
            raise ImproperlyConfigured(
                'The YouTubeOEmbedFinder should only work with the youtube provider'
            )

        super().__init__(providers=providers, options=options)

    def find_embed(self, url, max_width=None):
        embed = super().find_embed(url, max_width)

        soup = BeautifulSoup(embed['html'], 'html.parser')
        iframe_url = soup.find('iframe').attrs['src']
        scheme, netloc, path, params, query, fragment = urlparse(iframe_url)

        querydict = parse_qs(query)
        querydict['rel'] = 0
        query = urlencode(querydict, doseq=1)

        iframe_url = urlunparse((scheme, netloc, path, params, query, fragment))
        soup.find('iframe').attrs['src'] = iframe_url
        embed['html'] = str(soup)

        return embed
