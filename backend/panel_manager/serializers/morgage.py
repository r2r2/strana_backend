from rest_framework import serializers


class MortgagePanelLimits(serializers.Serializer):
    """Крайние значения по ипотечным предложениям в панели """
    max_rate = serializers.FloatField(label='максимальная ставка')
    min_rate = serializers.FloatField(label='минимальная ставка')
    max_term = serializers.FloatField(label='минимальный срок')
    min_term = serializers.FloatField(label='максимальный срок')
