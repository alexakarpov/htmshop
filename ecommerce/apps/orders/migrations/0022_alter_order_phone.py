# Generated by Django 4.2.16 on 2024-09-19 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_alter_order_shipping_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(default='888-888-8888', max_length=100),
            preserve_default=False,
        ),
    ]