# Generated by Django 3.0.10 on 2021-03-09 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0028_vacancypageformemployee'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancypageform',
            name='google_event_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Название ивента Google'),
        ),
    ]
