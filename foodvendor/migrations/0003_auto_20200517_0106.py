# Generated by Django 3.0.6 on 2020-05-17 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodvendor', '0002_auto_20200516_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='auth',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='auth',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
