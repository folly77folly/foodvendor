# Generated by Django 3.0.6 on 2020-05-16 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodvendor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='phone_number',
            field=models.CharField(max_length=11),
        ),
    ]