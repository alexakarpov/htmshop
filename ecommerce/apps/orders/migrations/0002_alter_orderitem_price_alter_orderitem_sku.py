# Generated by Django 4.2.2 on 2023-09-17 05:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_stock_sku'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=5),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='sku',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='inventory.stock'),
        ),
    ]
