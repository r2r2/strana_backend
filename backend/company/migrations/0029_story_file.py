# Generated by Django 3.0.10 on 2021-03-10 13:25

import ajaximage.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0028_story_storyimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='file',
            field=ajaximage.fields.AjaxImageField(blank=True, verbose_name='Обложка'),
        ),
    ]