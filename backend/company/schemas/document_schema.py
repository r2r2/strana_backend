from graphene import List, Node, ObjectType
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene_django.filter import DjangoFilterConnectionField
from common.graphene import ExtendedConnection
from common.schema import FacetFilterField, FacetWithCountType, SpecType
from ..filters import DocumentFilter
from ..models import Document, DocumentCategory


class DocumentType(OptimizedDjangoObjectType):
    """
    Тип документа
    """

    class Meta:
        model = Document
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = DocumentFilter


class DocumentCategoryType(OptimizedDjangoObjectType):
    """
    Тип категории документов
    """

    document_set = List(DocumentType)

    class Meta:
        model = DocumentCategory
        interfaces = (Node,)


class DocumentQuery(ObjectType):
    """
    Запросы документов
    """

    all_documents = DjangoFilterConnectionField(DocumentType, description="Фильтр по документам")
    all_document_categories = List(DocumentCategoryType, description="Список категорий документов")

    all_documents_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=DocumentType,
        filterset_class=DocumentFilter,
        method_name="facets",
        description="Фасеты для фильтра по документам",
    )
    all_documents_specs = FacetFilterField(
        List(SpecType),
        filtered_type=DocumentType,
        filterset_class=DocumentFilter,
        method_name="specs",
        description="Спеки для фильтра по документам",
    )

    document_category = Node.Field(DocumentCategoryType, description="Получение категории по ID")

    @staticmethod
    def resolve_all_documents(obj, info, **kwargs):
        return query(Document.objects.all(), info)

    @staticmethod
    def resolve_all_document_categories(obj, info, **kwargs):
        return query(DocumentCategory.objects.all(), info)
