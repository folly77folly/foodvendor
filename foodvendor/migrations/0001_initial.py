# Generated by Django 3.0.6 on 2020-05-13 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=60, unique=True)),
                ('password', models.CharField(max_length=50)),
                ('date_time_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=60, unique=True)),
                ('business_name', models.CharField(max_length=200)),
                ('phone_number', models.IntegerField()),
                ('date_time_created', models.DateTimeField(auto_now_add=True)),
                ('amount_outstanding', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=60, unique=True)),
                ('business_name', models.CharField(max_length=200)),
                ('phone_number', models.IntegerField()),
                ('date_time_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
