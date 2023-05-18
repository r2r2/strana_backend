from rest_framework import serializers

from ..models import Offer


class OfferSerializers(serializers.ModelSerializer):
    term = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    deposit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    payment = serializers.ReadOnlyField()

    class Meta:
        model = Offer
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
