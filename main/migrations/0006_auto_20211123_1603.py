# Generated by Django 3.2.8 on 2021-11-23 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20211123_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='sentiment',
            field=models.FloatField(default=-2),
        ),
    ]
