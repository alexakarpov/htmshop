# Generated by Django 4.2.16 on 2024-12-18 02:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0024_orderitem_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='title',
        ),
    ]