# Generated by Django 4.1.7 on 2023-03-25 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stock',
            old_name='quantity',
            new_name='wrapping_qty',
        ),
        migrations.AddField(
            model_name='stock',
            name='painting_qty',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stock',
            name='sanding_qty',
            field=models.IntegerField(default=0),
        ),
    ]