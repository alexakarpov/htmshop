# Generated by Django 4.2.16 on 2025-03-12 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_address_address_line2_alter_address_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='credit_limit',
            field=models.IntegerField(default=0),
        ),
    ]
