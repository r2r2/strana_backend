# Generated by Django 3.0.10 on 2021-09-13 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('commercial_project_page', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommercialProjectComparison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Очередность')),
            ],
            options={
                'verbose_name': 'Сравнение коммерческого проекта',
                'verbose_name_plural': 'Сравнения коммерческих проектов',
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='commercialprojectpage',
            name='invest_subtitle',
            field=models.CharField(blank=True, max_length=128, verbose_name='Подзаголовок блока инвестиций'),
        ),
        migrations.AddField(
            model_name='commercialprojectpage',
            name='invest_text',
            field=models.TextField(blank=True, verbose_name='Текст блока инвестиций'),
        ),
        migrations.AddField(
            model_name='commercialprojectpage',
            name='invest_title',
            field=models.CharField(blank=True, max_length=128, verbose_name='Заголовок блока инвестиций'),
        ),
        migrations.AddField(
            model_name='commercialprojectpage',
            name='video',
            field=models.URLField(blank=True, verbose_name='Видео о проекте'),
        ),
        migrations.AddField(
            model_name='commercialprojectpage',
            name='video_duration',
            field=models.CharField(default='2:30', max_length=30, verbose_name='Длительность видео'),
        ),
        migrations.CreateModel(
            name='CommercialProjectComparisonItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Название')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('subtitle', models.CharField(blank=True, max_length=200, verbose_name='Подзаголовок')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Очередность')),
                ('comparison', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='commercial_project_page.CommercialProjectComparison', verbose_name='Сравнение')),
            ],
            options={
                'verbose_name': 'Элемент сравнения коммерческого проекта',
                'verbose_name_plural': 'Элемент сравнения коммерческого проекта',
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='commercialprojectcomparison',
            name='commercial_project_page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commercial_project_page.CommercialProjectPage', verbose_name='Страница коммерческого проекта'),
        ),
        migrations.CreateModel(
            name='CommercialInvestCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Очередность')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('subtitle', models.CharField(blank=True, max_length=200, verbose_name='Подзаголовок')),
                ('image', models.ImageField(blank=True, null=True, upload_to='cpp/cic/i', verbose_name='Изображение')),
                ('commercial_project_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='commercial_project_page.CommercialProjectPage', verbose_name='Страница коммерческого проекта')),
            ],
            options={
                'verbose_name': 'Карточка инвестиций',
                'verbose_name_plural': 'Карточки инвестиций',
                'ordering': ('order',),
            },
        ),
    ]