# Generated by Django 4.2.13 on 2024-05-31 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_rename_sku_orderitem_stock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='paid',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipped',
        ),
    ]
