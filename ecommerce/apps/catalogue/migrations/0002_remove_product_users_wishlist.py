# Generated by Django 4.2.2 on 2023-08-18 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='users_wishlist',
        ),
    ]