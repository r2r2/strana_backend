from common import orm


class BaseRepo:
    q_builder: orm.QBuilder
    c_builder: orm.ConverterBuilder
    a_builder: orm.AnnotationBuilder
