# Generated by Django 4.2.2 on 2023-09-18 04:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_stock_sku'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='product_type',
        ),
        migrations.DeleteModel(
            name='ProductType',
        ),
    ]