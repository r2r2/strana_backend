# Generated by Django 3.1 on 2023-03-01 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('check', 'На проверке'), ('unique', 'Уникальный'), ('refused', 'Отказался'), ('not_unique', 'Не уникальный'), ('dispute', 'Оспаривание статуса'), ('can_dispute', 'Закреплен, но можно оспорить'), ('error', 'Ошибка')], max_length=50, verbose_name='Статус')),
                ('requested', models.DateTimeField(blank=True, null=True, verbose_name='Запрошено')),
                ('dispute_requested', models.DateTimeField(blank=True, null=True, verbose_name='Время оспаривания')),
                ('status_fixed', models.BooleanField(verbose_name='Закрепить статус за клиентом')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий агента')),
                ('admin_comment', models.TextField(blank=True, help_text='Внутренний комментарий (не отправляется агенту/клиенту)', null=True, verbose_name='Комментарий менеджера')),
            ],
            options={
                'verbose_name': 'Статус клиента',
                'verbose_name_plural': 'Статусы клиентов',
                'db_table': 'users_checks',
                'ordering': ['status', 'requested'],
                'managed': False,
            },
        ),
    ]