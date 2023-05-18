from rest_framework import serializers

from ..models import OfferPanel
from .nested import BankInOfferSerializer


class OfferPanelSerializers(serializers.ModelSerializer):
    term = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    deposit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    payment = serializers.ReadOnlyField()
    logo = serializers.ImageField(source="bank.logo")
    bank = BankInOfferSerializer(many=False, read_only=True)

    class Meta:
        model = OfferPanel
        exclude = ("projects", "city")

    @staticmethod
    def get_term(obj):
        if obj.term:
            return obj.term.upper

    @staticmethod
    def get_deposit(obj):
        if obj.deposit:
            return obj.deposit.upper

    @staticmethod
    def get_rate(obj):
        if obj.rate:
            return obj.rate.lower

    @staticmethod
    def get_amount(obj):
        if obj.amount:
            return obj.amount.upper
