from rest_framework.routers import DefaultRouter

from . import viewsets

panel_manager_router = DefaultRouter()

# # User
panel_manager_router.register("auth", viewsets.PanelAuthManagerViewSet, "panel_manager_auth")

# Clients
panel_manager_router.register("clients", viewsets.ClientViewSet, basename="panel_manager_clients")
panel_manager_router.register("meeting", viewsets.MeetingViewSet, basename="panel_manager_meeting")
panel_manager_router.register(
    "statistic", viewsets.StatisticViewSet, basename="panel_manager_statistic"
)

# Project
panel_manager_router.register(
    "project", viewsets.PanelManagerProjectViewSet, basename="panel_manager_project"
)
panel_manager_router.register(
    "about_project",
    viewsets.PanelManagerAboutProjectViewSet,
    basename="panel_manager_about_project",
)

# Property
panel_manager_router.register("flats", viewsets.PanelManagerFlatViewSet, "panel_manager_flats")
panel_manager_router.register(
    "favorites", viewsets.PanelManagerFavoritesViewSet, "panel_manager_favorites"
)


# Presentation
panel_manager_router.register(
    "presentation",
    viewsets.PanelManagerPresentationStageViewSet,
    basename="panel_manager_presentation",
)
panel_manager_router.register(
    "slides", viewsets.PanelManagerProjectGalleryViewSet, basename="panel_manager_slides"
)

# Progress
panel_manager_router.register(
    "progress", viewsets.PanelManagerProgressViewSet, basename="panel_manager_progress"
)
panel_manager_router.register(
    "camera", viewsets.PanelManagerCameraViewSet, basename="panel_manager_camera"
)

# Mortgage
panel_manager_router.register(
    "bank", viewsets.PanelManagerBankViewSet, basename="panel_manager_bank"
)
panel_manager_router.register(
    "offer", viewsets.PanelManagerOfferViewSet, basename="panel_manager_offer"
)

# infra
panel_manager_router.register(
    "infra-objects", viewsets.PanelManagerInfraObjectViewSet, basename="panel_manager_infra_objects"
)
panel_manager_router.register(
    "infra-categories",
    viewsets.PanelManagerInfraCategoryViewSet,
    basename="panel_manager_infra_categories",
)

# building
panel_manager_router.register(
    "building", viewsets.BuildingViewSet, basename="panel_manager_building"
)
# group section
panel_manager_router.register(
    "group_seciton", viewsets.GroupSectionViewSet, basename="panel_manager_group_seciton"
)
# section
panel_manager_router.register("seciton", viewsets.SectionViewSet, basename="panel_manager_seciton")
# floor
panel_manager_router.register("floor", viewsets.FloorViewSet, basename="panel_manager_floor")
