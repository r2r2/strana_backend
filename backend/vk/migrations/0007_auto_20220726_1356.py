# Generated by Django 3.0.14 on 2022-07-26 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vk', '0006_auto_20220721_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vkpost',
            name='published',
            field=models.BooleanField(default=False, verbose_name='Опубликовать пост на сайте'),
        ),
    ]
