# Generated by Django 3.0.10 on 2021-05-14 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("auction", "0005_auctionrules")]

    operations = [
        migrations.AddField(
            model_name="auction",
            name="current_price",
            field=models.IntegerField(db_index=True, default=0, verbose_name="Текущая цена"),
        )
    ]
