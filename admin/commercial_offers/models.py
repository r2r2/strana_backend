from django.db import models


class OfferSource(models.Model):

    name = models.CharField(verbose_name="Название источника", max_length=150)
    slug = models.CharField(verbose_name="Slug источника", max_length=32)

    def __repr__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "offers_offer_source"
        verbose_name = "Источник коммерческого предложения"
        verbose_name_plural = " 19.2. Источники коммерческого предложения"
        ordering = ['id']


class Offer(models.Model):

    booking_amo_id = models.IntegerField(verbose_name="ID сделки в АМО")
    client_amo_id = models.IntegerField(verbose_name="ID клиента в АМО")
    offer_link = models.CharField(max_length=250, null=True, verbose_name="Ссылка на КП в Тильда")
    created_at = models.DateTimeField(verbose_name="Дата и время создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата и время обновления", auto_now=True)
    uid = models.UUIDField(verbose_name="ID КП в АМО", null=True, blank=True)
    source = models.ForeignKey(
        "OfferSource",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="source_offers",
        verbose_name="Источник КП",
    )

    def __repr__(self):
        return f"{self.client_amo_id} - {self.booking_amo_id}"

    class Meta:
        managed = False
        db_table = "offers_offer"
        verbose_name = "Коммерческое предложение"
        verbose_name_plural = " 19.1. Коммерческие предложения"
        ordering = ['-id']


class OfferProperty(models.Model):

    offer = models.ForeignKey(
        "Offer",
        on_delete=models.CASCADE,
        related_name="offer_properties",
        verbose_name="Коммерческое предложение",
    )
    property_glogal_id = models.CharField(max_length=250, verbose_name="Global ID объекта собственности")

    def __repr__(self):
        return f'{self.offer.client_amo_id} - {self.offer.booking_amo_id} - {self.property_glogal_id}'

    class Meta:
        managed = False
        db_table = "offers_offer_property"
        verbose_name = "Объект собственности для КП"
        verbose_name_plural = " 19.3. Объекты собственности для КП"
        ordering = ['id']
