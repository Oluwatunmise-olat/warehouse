# Generated by Django 3.2.9 on 2021-11-26 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_controller', '0003_auto_20211125_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]