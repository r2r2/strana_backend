# Generated by Django 3.0.14 on 2022-06-21 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mortgage', '0023_auto_20220621_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='faq',
            field=models.ManyToManyField(blank=True, to='mortgage.OfferFAQ', verbose_name='FAQ'),
        ),
    ]
