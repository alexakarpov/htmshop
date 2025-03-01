# Generated by Django 4.2.16 on 2024-12-16 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_alter_stock_options_stock_is_set_alter_stock_sku'),
        ('orders', '0022_alter_order_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='stock',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock', to='inventory.stock'),
        ),
    ]
