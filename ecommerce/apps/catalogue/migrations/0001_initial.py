# Generated by Django 4.2.2 on 2023-07-23 07:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Required and unique', max_length=255, unique=True, verbose_name='Category Name')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Category safe URL')),
                ('is_active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='catalogue.category')),
            ],
            options={
                'verbose_name_plural': 'categories',
                'unique_together': {('slug', 'parent')},
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alt_text', models.CharField(blank=True, help_text='Please add alternative text', max_length=255, null=True, verbose_name='Alternative text')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Required', max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, help_text='Not Required', verbose_name='description')),
                ('slug', models.SlugField(max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Change product visibility', verbose_name='Product visibility')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('image', models.ImageField(default='images/default.png', help_text='Upload a product image', upload_to='images/', verbose_name='image')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalogue.category')),
                ('users_wishlist', models.ManyToManyField(blank=True, related_name='user_wishlist', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ('-created_at',),
            },
        ),
    ]
