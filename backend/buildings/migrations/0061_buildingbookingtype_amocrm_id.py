# Generated by Django 3.0.14 on 2022-09-22 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0060_auto_20220804_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildingbookingtype',
            name='amocrm_id',
            field=models.BigIntegerField(null=True, verbose_name='Идентификатор АМОЦРМ'),
        ),
    ]
