# Generated by Django 3.1.2 on 2023-04-26 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20230426_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='color',
            name='color',
            field=models.IntegerField(default=16777, max_length=8, verbose_name='код (десятичный)'),
        ),
    ]