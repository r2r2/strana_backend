# Generated by Django 3.0.14 on 2022-09-08 08:29

from django.db import migrations


def get_vacancies(apps, schema_editor):

    vacancy_category = apps.get_model('vacancy', 'VacancyCategory')
    company_category = apps.get_model('company', 'VacancyCategory')

    for cat in company_category.objects.all():
        vacancy_category.objects.create(
            name=cat.name,
            order=cat.order,
        )

    vacancy = apps.get_model('vacancy', 'Vacancy')
    company = apps.get_model('company', 'Vacancy')

    for row in company.objects.all():
        v = vacancy.objects.create(
            job_title=row.job_title,
            announcement=row.announcement,
            duties=row.duties,
            requirements=row.requirements,
            conditions=row.conditions,
            date=row.date,
            order=row.order,
            is_active=row.is_active,
            work_format=row.work_format,
            category=vacancy_category.objects.filter(name=row.category.name).first()
        )
        ids = row.city.values_list('id', flat=True)
        if ids:
            [v.city.add(_id) for _id in ids]


class Migration(migrations.Migration):

    dependencies = [
        ('vacancy', '0007_auto_20220907_1937'),
    ]

    operations = [
        migrations.RunPython(get_vacancies, reverse_code=migrations.RunPython.noop),
    ]