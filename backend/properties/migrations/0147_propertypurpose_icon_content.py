# Generated by Django 3.0.14 on 2022-09-01 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0146_auto_20220901_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertypurpose',
            name='icon_content',
            field=models.TextField(blank=True, null=True, verbose_name='Контент иконки'),
        ),
    ]