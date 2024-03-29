# Generated by Django 3.0.10 on 2021-08-12 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0039_auto_20210810_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='residential_set',
            field=models.ManyToManyField(blank=True, help_text='Привязывает коммерческие к жилым помещениям', limit_choices_to={'kind': 'RESIDENTIAL'}, to='buildings.Building', verbose_name='Жилое строение'),
        ),
    ]
