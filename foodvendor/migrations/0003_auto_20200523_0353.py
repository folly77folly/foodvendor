# Generated by Django 3.0.6 on 2020-05-23 03:53

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('foodvendor', '0002_auto_20200523_0339'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='auth',
            name='date_expiry',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 5, 23, 4, 3, 37, 720708, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='orders',
            name='cancel_expiry',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 5, 23, 4, 3, 37, 728726, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='orders',
            name='delivery_date_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 5, 23, 3, 53, 37, 728816, tzinfo=utc)),
        ),
    ]
