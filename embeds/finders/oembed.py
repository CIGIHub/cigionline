from bs4 import BeautifulSoup
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from wagtail.embeds.finders.oembed import OEmbedFinder
from wagtail.embeds.oembed_providers import youtube


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
