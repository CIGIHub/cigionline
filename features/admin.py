from wagtail_modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from .models import (
    HomePageFeaturedPromotionsList,
    HomePageFeaturedContentList,
    HomePageFeaturedPublicationsList,
    HomePageFeaturedExpertsList,
    HomePageFeaturedMultimediaList,
    HomePageFeaturedHighlightsList,
    HomePageFeaturedEventsList,
)


class HomePageFeaturedContentListModelAdmin(ModelAdmin):
    model = HomePageFeaturedContentList
    menu_label = 'Home Page Featured Content'
    menu_icon = 'doc-empty'
    menu_order = 201


class HomePageFeaturedPublicationsListModelAdmin(ModelAdmin):
    model = HomePageFeaturedPublicationsList
    menu_label = 'Home Page Featured Publications'
    menu_icon = 'doc-full'
    menu_order = 202


class HomePageFeaturedHighlightsListModelAdmin(ModelAdmin):
    model = HomePageFeaturedHighlightsList
    menu_label = 'Home Page Featured Highlights'
    menu_icon = 'doc-empty-inverse'
    menu_order = 203


class HomePageFeaturedMultimediaListModelAdmin(ModelAdmin):
    model = HomePageFeaturedMultimediaList
    menu_label = 'Home Page Featured Multimedia'
    menu_icon = 'media'
    menu_order = 204


class HomePageFeaturedExpertsListModelAdmin(ModelAdmin):
    model = HomePageFeaturedExpertsList
    menu_label = 'Home Page Featured Experts'
    menu_icon = 'group'
    menu_order = 205


class HomePageFeaturedEventsListModelAdmin(ModelAdmin):
    model = HomePageFeaturedEventsList
    menu_label = 'Home Page Featured Events'
    menu_icon = 'date'
    menu_order = 206


class HomePageFeaturedPromotionsListModelAdmin(ModelAdmin):
    model = HomePageFeaturedPromotionsList
    menu_label = 'Home Page Featured Promotions'
    menu_icon = 'image'
    menu_order = 207


class FeaturesModelAdminGroup(ModelAdminGroup):
    menu_label = 'Features'
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    items = (
        HomePageFeaturedContentListModelAdmin,
        HomePageFeaturedPublicationsListModelAdmin,
        HomePageFeaturedHighlightsListModelAdmin,
        HomePageFeaturedMultimediaListModelAdmin,
        HomePageFeaturedExpertsListModelAdmin,
        HomePageFeaturedEventsListModelAdmin,
        HomePageFeaturedPromotionsListModelAdmin,
    )


modeladmin_register(FeaturesModelAdminGroup)
