# Generated by Django 4.1.3 on 2023-01-01 06:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productinventory',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productinventory',
            name='product_type',
        ),
        migrations.RemoveField(
            model_name='productinventory',
            name='specifications',
        ),
        migrations.RemoveField(
            model_name='productspecification',
            name='product_type',
        ),
        migrations.RemoveField(
            model_name='productspecificationvalue',
            name='sku',
        ),
        migrations.RemoveField(
            model_name='productspecificationvalue',
            name='specification',
        ),
    ]