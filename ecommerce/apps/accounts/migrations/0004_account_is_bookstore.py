# Generated by Django 4.2.2 on 2023-12-24 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rename_address_line_address_address_line1'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_bookstore',
            field=models.BooleanField(default=False),
        ),
    ]
