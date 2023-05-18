from rest_framework import serializers

from ..models import Bank
from .offers_panel_serializers import OfferPanelSerializers


class BankSerializers(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()
    term = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    offerpanel_set = OfferPanelSerializers(many=True)

    class Meta:
        model = Bank
        fields = "__all__"

    def get_rate(self, obj: Bank):
        return getattr(obj, "min_rate", None)

    def get_term(self, obj: Bank):
        return getattr(obj, "max_term", None)

    def get_payment(self, obj: Bank):
        return getattr(obj, "payment", None)
