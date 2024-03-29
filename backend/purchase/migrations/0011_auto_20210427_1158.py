# Generated by Django 3.0.10 on 2021-04-27 11:58

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0010_purchasetype_is_commercial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Заголовок')),
            ],
            options={
                'verbose_name': 'Размер оплаты',
                'verbose_name_plural': 'Размеры оплаты',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='PurchaseAmountDescriptionBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Заголовок')),
                ('description', ckeditor.fields.RichTextField(blank=True, verbose_name='Описание')),
                ('amount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchase.PurchaseAmount', verbose_name='Размер оплаты')),
            ],
            options={
                'verbose_name': 'Размер оплаты, блок описания',
                'verbose_name_plural': 'Размер оплаты, блоки описания',
                'ordering': ('id',),
            },
        ),
        migrations.AddField(
            model_name='purchasetype',
            name='amount',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchase.PurchaseAmount', verbose_name='Размер оплаты'),
        ),
    ]
