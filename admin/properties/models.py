from django.db import models


class Property(models.Model):
    """
    Объект недвижимости
    """

    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    article = models.CharField(max_length=50, blank=True, null=True)
    plan = models.ImageField(max_length=300, blank=True, null=True, upload_to="p/p/p")
    plan_png = models.ImageField(max_length=300, blank=True, null=True, upload_to="p/p/pp")
    price = models.BigIntegerField(blank=True, null=True)
    original_price = models.BigIntegerField(blank=True, null=True)
    final_price = models.BigIntegerField(blank=True, null=True)
    area = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    deadline = models.CharField(max_length=50, blank=True, null=True)
    discount = models.BigIntegerField(blank=True, null=True)
    project = models.ForeignKey("projects.Project", models.CASCADE, blank=True, null=True)
    floor = models.ForeignKey("floors.Floor", models.CASCADE, blank=True, null=True)
    building = models.ForeignKey("buildings.Building", models.CASCADE, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    rooms = models.SmallIntegerField(blank=True, null=True)
    premise = models.CharField(max_length=30, blank=True, null=True)
    total_floors = models.SmallIntegerField(blank=True, null=True)
    special_offers = models.TextField(null=True, blank=True)
    similar_property_global_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.article) if self.article else str(self.id)  # pylint: disable=no-member

    class Meta:
        managed = False
        db_table = "properties_property"
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"
