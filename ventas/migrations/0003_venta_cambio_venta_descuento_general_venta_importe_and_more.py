# Generated by Django 5.1.6 on 2025-03-27 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0002_remove_venta_vendedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='cambio',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='venta',
            name='descuento_general',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='venta',
            name='importe',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='venta',
            name='metodo_pago',
            field=models.CharField(default='efectivo', max_length=20),
        ),
    ]
