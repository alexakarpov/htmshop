# Generated by Django 4.1.6 on 2023-02-11 03:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_stock_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productinventory',
            name='quantity',
        ),
    ]
