# Generated by Django 3.0.10 on 2021-03-26 08:46

from django.db import migrations


def forwards(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    City = apps.get_model("cities", "City")
    Manager = apps.get_model("request_forms", "Manager")
    city_qs = City.objects.filter(active=True)
    manager_qs = Manager.objects.using(db_alias).all()
    for manager in manager_qs:
        for city in city_qs:
            manager.cities.add(city)
            manager.save()


def reverse(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Manager = apps.get_model("request_forms", "Manager")
    manager_qs = Manager.objects.using(db_alias).all()
    for manager in manager_qs:
        manager.cities.clear()
        manager.save()


class Migration(migrations.Migration):

    dependencies = [
        ('request_forms', '0036_auto_20210325_1440'),
    ]

    operations = [migrations.RunPython(forwards, reverse_code=reverse)]