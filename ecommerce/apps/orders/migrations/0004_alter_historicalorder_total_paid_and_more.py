# Generated by Django 4.2.2 on 2023-09-22 01:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalorder',
            name='total_paid',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_paid',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=7),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid_at', models.DateTimeField(auto_now=True)),
                ('comment', models.CharField(blank=True, max_length=150, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='orders.order')),
            ],
        ),
    ]
