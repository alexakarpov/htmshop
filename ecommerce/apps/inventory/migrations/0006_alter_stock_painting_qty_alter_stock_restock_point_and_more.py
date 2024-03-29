# Generated by Django 4.2.2 on 2023-10-20 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_stock_product_type_delete_producttype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='painting_qty',
            field=models.IntegerField(default=0, verbose_name='Painting room stock'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='restock_point',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='stock',
            name='sanding_qty',
            field=models.IntegerField(default=0, verbose_name='Sanding room stock'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='target_amount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='stock',
            name='wrapping_qty',
            field=models.IntegerField(default=0, verbose_name='Wrapping room stock'),
        ),
    ]
