from rest_framework import serializers

from projects.models import Project
from mortgage.models import Bank, OfferPanel, Program
from mortgage.constants import MortgageType


class ProjectDvizhSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="dvizh_uuid")
    externalId = serializers.IntegerField(source="dvizh_id")

    class Meta:
        model = Project
        fields = ["uuid", "externalId"]


class BankDvizhSerializer(serializers.ModelSerializer):
    externalId = serializers.IntegerField(source="dvizh_id")

    class Meta:
        model = Bank
        fields = ["name", "externalId"]


class OfferDvizhSerializer(serializers.ModelSerializer):
    bankId = serializers.IntegerField()
    program_type = serializers.CharField()
    agenda_type = serializers.CharField()
    maxCreditAmount = serializers.IntegerField(source="amount")
    maxCreditPeriod = serializers.IntegerField(source="term")
    minInitialPayment = serializers.IntegerField(source="deposit")


    class Meta:
        model = OfferPanel
        fields = [
            "city",
            "bankId",
            "program_type",
            "rate",
            "agenda_type",
            "maxCreditAmount",
            "maxCreditPeriod",
            "minInitialPayment",
        ]

    @staticmethod
    def validate_rate(value):
        return value, None

    @staticmethod
    def validate_maxCreditAmount(value):
        amount = int(value // 100)
        if 2_147_483_647 < amount:
            return None
        return None, amount

    @staticmethod
    def validate_maxCreditPeriod(value):
        return None, value / 12

    @staticmethod
    def validate_minInitialPayment(value):
        return value, None

    def to_internal_value(self, data):
        ret = super(OfferDvizhSerializer, self).to_internal_value(data)
        agenda_type = ret.pop("agenda_type")
        program_type = ret.pop("program_type")
        if agenda_type == "primary_housing":
            ret["type"] = MortgageType.RESIDENTIAL
            ret["program_id"] = Program.objects.filter(dvizh_type=program_type).first().id
        else:
            ret["type"] = MortgageType.COMMERCIAL
            ret["program_id"] = Program.objects.filter(name="Коммерческая недвижимость").first().id
        ret["bank_id"] = Bank.objects.filter(dvizh_id=ret.pop("bankId")).first().id
        return ret
