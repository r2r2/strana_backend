from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene import ObjectType, Node
from graphene_django.filter import DjangoFilterConnectionField

from .models import Experiment
from .filters import ExperimentFilter


class ExperimentType(OptimizedDjangoObjectType):
    """
    Тип эксперемента
    """

    class Meta:
        model = Experiment
        interfaces = (Node,)
        filterset_class = ExperimentFilter


class ExperimentQuery(ObjectType):
    """
    Запросы эксперементов
    """
    experiments = DjangoFilterConnectionField(ExperimentType, description="Эксперементы")

    @staticmethod
    def resolve_experiments(obj, info, **kwargs):
        return query(Experiment.objects.filter(is_active=True), info)

