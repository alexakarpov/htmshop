# Generated by Django 4.2.2 on 2024-02-06 01:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_delete_historicalorder'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='city',
            new_name='city_locality',
        ),
    ]
