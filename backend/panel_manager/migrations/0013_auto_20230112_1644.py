# Generated by Django 3.0.14 on 2023-01-12 13:44

from django.db import migrations
from django.db.models import Q

def add_initial_roles(apps, schema_editor):
    Manager: 'Manager' = apps.get_model('panel_manager', 'Manager')
    Role: 'Role' = apps.get_model('panel_manager', 'Role')
    role = Role.objects.create(
        name='can_manage_meetings', description='может управлять встречами'
    )
    email_list = (
        'Olga.Voronova@strana.com',
        'Maksim.Tiumentsev@strana.com',
        'amanzhol.elimbaev@strana.com',
        'any@mailedelweiss1304.ru'
    )
    email_filter = Q()
    for email in email_list:
        email_filter |= Q(login__iexact=email) | Q(user__email__iexact=email)
    for manager in Manager.objects.filter(email_filter).order_by('id').distinct('id').all():
        manager.roles.add(role)


def remove_initial_roles(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('panel_manager', '0012_auto_20230112_1643'),
    ]

    operations = [
        migrations.RunPython(add_initial_roles, reverse_code=remove_initial_roles)
    ]