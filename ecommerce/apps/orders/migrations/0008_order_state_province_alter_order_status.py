# Generated by Django 4.2.1 on 2023-06-26 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='state_province',
            field=models.CharField(default='NH', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PENDING', 'pending'), ('PROCESSING', 'processing'), ('SHIPPED', 'shipped'), ('CANCELED', 'canceled'), ('RETURNED', 'returned')], default='PENDING', max_length=10),
        ),
    ]