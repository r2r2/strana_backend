# Generated by Django 3.0.10 on 2021-05-12 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("auction", "0002_auto_20210512_0947")]

    operations = [
        migrations.AlterModelOptions(
            name="notification",
            options={
                "verbose_name": "Уведомление аукциона",
                "verbose_name_plural": "Уведомления аукциона",
            },
        )
    ]
