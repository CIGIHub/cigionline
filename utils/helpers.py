from wagtail.models import Page


class CreatePage:
    def __init__(self, page_model, page_title, parent_page_title):
        self.page_model = page_model
        self.page_title = page_title
        self.parent_page_title = parent_page_title

    def page_exists(self):
        return self.page_model.objects.filter(title=self.page_title).exists()

    def parent_page_exists(self):
        return Page.objects.filter(title=self.parent_page_title).exists()

    def create_page(self):
        if self.parent_page_exists():
            parent_page = Page.objects.get(title=self.parent_page_title)
            if not self.page_exists():
                page = self.page_model(title=self.page_title)
                parent_page.add_child(instance=page)
            return self.page_model.objects.get(title=self.page_title)


class CreateContentPage(CreatePage):
    def __init__(self, page_model, page_title, parent_page_title, publishing_date):
        super().__init__(page_model, page_title, parent_page_title)
        self.publishing_date = publishing_date

    def create_contentpage(self):
        if self.parent_page_exists():
            if not self.page_exists():
                parent_page = Page.objects.get(title=self.parent_page_title)
                page = self.page_model(title=self.page_title, publishing_date=self.publishing_date)
                parent_page.add_child(instance=page)
            return self.page_model.objects.get(title=self.page_title)


class CreateArticlePage(CreateContentPage):
    def __init__(self, page_model, page_title, parent_page_title, publishing_date, article_type):
        super().__init__(page_model, page_title, parent_page_title, publishing_date)
        self.article_type = article_type

    def create_article_page(self):
        if self.parent_page_exists():
            if not self.page_exists():
                parent_page = Page.objects.get(title=self.parent_page_title)
                page = self.page_model(title=self.page_title, publishing_date=self.publishing_date, article_type=self.article_type)
                parent_page.add_child(instance=page)
            return self.page_model.objects.get(title=self.page_title)
