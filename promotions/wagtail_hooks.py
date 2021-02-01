from .models import PromotionBlock
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)


class PromotionBlockModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PromotionBlock
    menu_label = 'Promotion Blocks'
    menu_icon = 'image'
    menu_order = 900
    list_display = ('name', 'block_type')
    list_filter = ('block_type',)
    search_fields = ('name',)


modeladmin_register(PromotionBlockModelAdmin)
