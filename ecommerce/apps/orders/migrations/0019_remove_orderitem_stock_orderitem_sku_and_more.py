# Generated by Django 4.2.13 on 2024-07-25 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_order_is_bookstore_order_alter_order_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='stock',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='sku',
            field=models.CharField(default='A-123', max_length=40, verbose_name='Product SKU'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_method',
            field=models.CharField(choices=[('REGULAR', 'Regular'), ('FAST', 'Fast'), ('EXPEDITED', 'Expedited')], max_length=20),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
    ]