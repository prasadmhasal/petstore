# Generated by Django 5.0 on 2023-12-14 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='time',
            field=models.TimeField(auto_now=True, null=True),
        ),
    ]
