# Generated by Django 4.2.13 on 2024-07-15 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_alter_order_order_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=777, max_digits=7),
            preserve_default=False,
        ),
    ]
