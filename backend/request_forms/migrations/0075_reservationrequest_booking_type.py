# Generated by Django 3.0.14 on 2022-01-10 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0048_auto_20220110_1848'),
        ('request_forms', '0074_advantageformrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationrequest',
            name='booking_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='buildings.BuildingBookingType', verbose_name='Тип бронирования'),
        ),
    ]