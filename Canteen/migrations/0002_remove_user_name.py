# Generated by Django 4.2.4 on 2023-08-21 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Canteen', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
    ]
