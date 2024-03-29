# Generated by Django 3.0.14 on 2021-12-28 13:02

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0102_project_presentation'),
        ('request_forms', '0073_auto_20211220_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvantageFormRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='Номер')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время отправки')),
                ('property_type', models.CharField(blank=True, choices=[('flat', 'Квартира'), ('parking', 'Парковочное место'), ('commercial', 'Коммерческое помещение'), ('pantry', 'Кладовка'), ('commercial_apartment', 'Аппартаменты коммерции')], max_length=20, verbose_name='Тип')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.Project', verbose_name='Проект')),
            ],
            options={
                'verbose_name': 'Заявка с формы УТП',
                'verbose_name_plural': 'Заявки с формы УТП',
            },
        ),
    ]
