# Generated by Django 3.0.14 on 2022-10-24 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel_manager', '0007_auto_20220919_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='id_crm',
            field=models.CharField(blank=True, help_text='ID лида в AmoCRM', max_length=200, verbose_name='ID в AmoCRM'),
        ),
    ]
