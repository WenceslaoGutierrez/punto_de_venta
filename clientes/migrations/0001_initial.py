# Generated by Django 5.1.6 on 2025-03-11 20:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('negocio', '0002_datosfiscales_remove_negocio_razon_social_and_more'),
        ('usuarios', '0005_alter_datoscontacto_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datos_contacto', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.datoscontacto')),
                ('datos_fiscales', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='negocio.datosfiscales')),
                ('datos_personales', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.datospersonales')),
                ('domicilios', models.ManyToManyField(blank=True, to='negocio.datosdomicilio')),
            ],
        ),
    ]
