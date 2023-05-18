from django.db import models


class Agency(models.Model):
    """
    Агентство
    """

    inn = models.CharField(max_length=30)
    city = models.CharField(max_length=30, verbose_name="Город агентства")
    is_approved = models.BooleanField(verbose_name="Подтверждено")
    is_deleted = models.BooleanField(verbose_name="Удалено")
    type = models.CharField(max_length=20, blank=True, null=True)
    files = models.JSONField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    amocrm_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    state_registration_number = models.CharField(verbose_name="ОГРН/ОРНИП", max_length=15, null=True, blank=True)
    legal_address = models.TextField(verbose_name="Юридически адрес", null=True, blank=True)
    bank_name = models.CharField(verbose_name="Название банка", max_length=100, null=True, blank=True)
    bank_identification_code = models.CharField(verbose_name="БИК", max_length=9, null=True, blank=True)
    checking_account = models.CharField(verbose_name="Расчетный счет", max_length=20, null=True, blank=True)
    correspondent_account = models.CharField(verbose_name="Корреспондентский счет", max_length=20,
                                             null=True, blank=True)

    signatory_name = models.CharField(verbose_name="Имя подписанта", max_length=50, null=True, blank=True)
    signatory_surname = models.CharField(verbose_name="Фамилия подписанта", max_length=50, null=True, blank=True)
    signatory_patronymic = models.CharField(verbose_name="Отчество подписанта", max_length=50, null=True, blank=True)
    signatory_registry_number = models.CharField(verbose_name="Номер регистрации в реестре",
                                                 max_length=100, null=True, blank=True)
    signatory_sign_date = models.DateField(verbose_name="Дата подписания", null=True, blank=True)

    def __str__(self):
        return self.name if self.name else self.id

    class Meta:
        managed = False
        db_table = "agencies_agency"
        verbose_name = "Агентство"
        verbose_name_plural = "Агентства"
        ordering = ["-created_at"]
