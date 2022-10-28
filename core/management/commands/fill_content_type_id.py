from django.core.management.base import BaseCommand
from django.db.models import F, Func, Value, JSONField
from wagtail.models import PageRevision


class Command(BaseCommand):
    def handle(self, *args, **options):
        def unique_content_types_missing():
            return set(PageRevision.objects.exclude(content__has_key='content_type').select_related('page').values_list('page__content_type_id', flat=True))

        def update_field(objs, content_type_id):
            print(f'now updating content type: {content_type_id}')
            print(f'the following {len(objs)} rows are affected: {list(objs.values_list("id", flat=True))}')
            initial_length = len(objs)
            objs.update(
                content=Func(
                    F('content'),  # target JSON
                    Value(["content_type"]),  # key
                    Value(content_type_id, JSONField()),  # new value
                    True,  # whether to create if key does not exist
                    function='jsonb_set',
                )
            )
            return (initial_length)

        rows_affected = 0
        for content_type_id in unique_content_types_missing():
            rows_affected += update_field(
                PageRevision.objects.exclude(content__has_key='content_type').select_related('page').filter(page__content_type_id=content_type_id).order_by('id'),
                content_type_id
            )
        print(f'total rows affected: {rows_affected}')
