# Generated by Django 3.0.14 on 2022-07-14 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vkpostimages',
            name='id_image',
            field=models.CharField(db_index=True, default='', max_length=200, verbose_name='ID картинки'),
            preserve_default=False,
        ),
    ]