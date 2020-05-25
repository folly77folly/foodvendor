# Generated by Django 3.0.6 on 2020-05-23 15:55

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('foodvendor', '0007_auto_20200523_1324'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='order',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='order_status',
        ),
        migrations.AddField(
            model_name='notification',
            name='message_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='foodvendor.MessageStatus'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='auth',
            name='date_expiry',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 5, 23, 16, 5, 30, 397140, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='orders',
            name='cancel_expiry',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 5, 23, 16, 5, 30, 403955, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='orders',
            name='delivery_date_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 5, 23, 15, 55, 30, 404028, tzinfo=utc)),
        ),
    ]
