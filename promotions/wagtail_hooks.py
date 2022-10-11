from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)
from wagtail import hooks

from .models import PromotionBlock


@hooks.register('register_permissions')
def register_promotion_block_permissions():
    permission_block_content_type = ContentType.objects.get(app_label='promotions', model='promotionblock')
    return Permission.objects.filter(content_type=permission_block_content_type)


class PromotionBlockModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PromotionBlock
    menu_label = 'Promotion Blocks'
    menu_icon = 'image'
    menu_order = 203
    list_display = ('name', 'block_type')
    list_filter = ('block_type',)
    search_fields = ('name',)


modeladmin_register(PromotionBlockModelAdmin)
