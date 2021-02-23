from wagtail.search import index


class AuthorFilterField(index.FilterField):
    def get_attname(self, cls):
        return self.field_name

    def get_type(self, cls):
        return 'IntegerField'

    def get_value(self, obj):
        return list(getattr(obj, self.field_name).all().values_list('author__id', flat=True))


class ParentalManyToManyFilterField(index.FilterField):
    def get_attname(self, cls):
        return self.field_name

    def get_type(self, cls):
        return 'IntegerField'

    def get_value(self, obj):
        return list(getattr(obj, self.field_name).all().values_list('id', flat=True))


class ParentalManyToManyFilterFieldName(index.FilterField):
    def get_attname(self, cls):
        return self.field_name

    def get_type(self, cls):
        return 'CharField'

    def get_value(self, obj):
        return list(getattr(obj, self.field_name).all().values_list('name', flat=True))
