from rest_framework import serializers

from mortgage.models import Bank


class BankInOfferSerializer(serializers.ModelSerializer):
    """Выделенный сериализатор представления банка в предложении."""
    class Meta:
        model = Bank
        fields = "__all__"
