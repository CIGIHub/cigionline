from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from .models import HomePageFeaturedPromotionsPage, HomePageFeaturedContentList


class HomePageFeaturedPromotionsPageModelAdmin(ModelAdmin):
    model = HomePageFeaturedPromotionsPage
    menu_label = 'Home Page Featured Promotions'
    menu_icon = 'image'
    menu_order = 204


class HomePageFeaturedContentListModelAdmin(ModelAdmin):
    model = HomePageFeaturedContentList
    menu_label = 'Home Page Featured Content'
    menu_icon = 'image'
    menu_order = 205


class FeaturesModelAdminGroup(ModelAdminGroup):
    menu_label = 'Features'
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    items = (
        HomePageFeaturedPromotionsPageModelAdmin,
        HomePageFeaturedContentListModelAdmin
    )


modeladmin_register(FeaturesModelAdminGroup)
