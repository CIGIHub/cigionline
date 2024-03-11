
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from django.core.management.base import BaseCommand
from articles.models import ArticlePage
from wagtail.models import Page

class Command(BaseCommand):
    help = 'Check for broken links in ArticlePage instances'
    
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
    }
    
    ignore = [
      'https://twitter.com/cigionline',
      'https://www.linkedin.com/company/cigionline/',
      'https://twitter.com/share?'
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Checking for broken links..."))
        base_url = input("Enter the base URL of your Wagtail site: ")
        broken_links = self.crawl_site(base_url)
        self.stdout.write(self.style.SUCCESS("Broken links:"))
        for page_url, page_id, link_url in broken_links:
            self.stdout.write(f"Page URL: {page_url}, Page id: {page_id}, Broken Link: {link_url}")

    def get_links_from_page(self, url):
        try:
          response = requests.get(url, timeout=10)
          soup = BeautifulSoup(response.text, 'html.parser')
          body_content = soup.find(class_='body')
          links = []
          for link in body_content.find_all('a'):
              href = link.get('href')
              if href:
                  links.append(href)
          return links
        except Exception as e:
            self.stderr.write(f"Error getting links from {url}: {e}")
            return []

    def check_link(self, url):
        try:
            response = requests.get(url, headers=self.headers, allow_redirects=True, timeout=10)
            response.raise_for_status()
            return {
              'code': response.status_code < 400,
              'status': response.status_code
            }
        except Exception as e:
            self.stderr.write(f"Error checking {url}: {e}")
            return {
              'code': False,
              'status': 0
            }

    def crawl_site(self, base_url):
        broken_links = set()

        def crawl(page):
            self.stdout.write(f"Checking links on page: {page.url}, page id: {page.id}, publishing date: {page.publishing_date}")
            links = self.get_links_from_page(page.url)
            for link in links:
                if any([i in link for i in self.ignore]):
                    continue
                absolute_url = urljoin(base_url, link)
                if not urlparse(absolute_url).netloc:
                    continue
                response = self.check_link(absolute_url)
                if not response['code']:
                    broken_links.add((page.url, page.id, absolute_url))
                    self.stderr.write(f"Page URL: {page.url}, id: {page.id}, status: {response['status']}, Broken Link: {link}")

        all_pages = ArticlePage.objects.live().public().filter(id__gt=13446)        
        
        for page in all_pages:
            crawl(page)

        return broken_links