from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from typing import Type

from panel_manager.filters import AboutProjectFilter
from panel_manager.models import (
    OurProjects,
    ProjectsForMap,
    StageProjects,
    AboutProject,
    AboutProjectGalleryCategory,
)
from panel_manager.serializers import (
    OurProjectsSerializer,
    ProjectsForMapSerializer,
    StageProjectsSerializer,
    AboutProjectSeriazlier,
    AboutProjectGalleryCategorySeriazlier,
)


class PanelManagerAboutProjectViewSet(ReadOnlyModelViewSet):
    """
    О проекте
    """

    permission_classes: tuple[Type[BasePermission]] = (AllowAny,)
    queryset = AboutProjectGalleryCategory.objects.all()
    filterset_class = AboutProjectFilter
    pagination_class = None
    serializer_class = AboutProjectGalleryCategorySeriazlier
    filter_backends = (DjangoFilterBackend,)

    @action(detail=False)
    def our_projects(self, request, *args, **kwargs):
        """Наши проекты"""
        our_projects = OurProjects.get_solo()
        projects = ProjectsForMap.objects.all().select_related("stage", "our_project")
        stage = StageProjects.objects.all()
        data = {
            "our_project": OurProjectsSerializer(
                instance=our_projects, context={"request": request}
            ).data,
            "projects": ProjectsForMapSerializer(
                projects, many=True, read_only=True, context={"request": request}
            ).data,
            "stage": StageProjectsSerializer(
                stage, many=True, read_only=True, context={"request": request}
            ).data,
        }
        return Response(data=data)

    @action(detail=False)
    def about_project(self, request, *args, **kwargs):
        """О проекте"""
        about_project = (
            AboutProject.objects.all().prefetch_related("aboutprojectparametrs_set").first()
        )
        data = AboutProjectSeriazlier(instance=about_project, context={"request": request}).data
        return Response(data=data)
