# Generated by Django 3.0.10 on 2021-05-18 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("projects", "0063_merge_20210409_1631"), ("news", "0021_remove_news_projects")]

    operations = [
        migrations.AddField(
            model_name="news",
            name="projects",
            field=models.ManyToManyField(blank=True, to="projects.Project", verbose_name="Проекты"),
        )
    ]