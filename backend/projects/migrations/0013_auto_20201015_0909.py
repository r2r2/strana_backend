# Generated by Django 3.0.10 on 2020-10-15 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0012_auto_20201014_0910"),
    ]

    operations = [
        migrations.RemoveField(model_name="finishingpoint", name="finishing",),
        migrations.RemoveField(model_name="project", name="finishing",),
        migrations.DeleteModel(name="Finishing",),
        migrations.DeleteModel(name="FinishingCategory",),
        migrations.DeleteModel(name="FinishingPoint",),
        migrations.DeleteModel(name="FinishingTab",),
    ]
