# Generated by Django 4.2.1 on 2023-06-02 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_order_key'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='billing_status',
            new_name='paid',
        ),
    ]