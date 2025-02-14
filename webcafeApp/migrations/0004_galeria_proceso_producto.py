# Generated by Django 3.0.1 on 2020-09-01 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webcafeApp', '0003_auto_20200901_0939'),
    ]

    operations = [
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, null=True, verbose_name='Tipo de Producto')),
                ('descripcion', models.TextField(null=True, verbose_name='Descripción')),
                ('imagen', models.ImageField(null=True, upload_to='static/upload', verbose_name='Imagen')),
            ],
        ),
        migrations.CreateModel(
            name='Proceso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, null=True, verbose_name='Tipo de Proceso')),
                ('descripcion', models.TextField(null=True, verbose_name='Descripción')),
                ('imagen', models.ImageField(null=True, upload_to='static/upload', verbose_name='Imagen')),
                ('tipo_producto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='webcafeApp.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='Galeria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now=True, verbose_name='Fecha')),
                ('titulo', models.CharField(max_length=150, verbose_name='Título')),
                ('imagen', models.ImageField(upload_to='static/upload/galeria', verbose_name='Imagen')),
                ('producto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='webcafeApp.Producto')),
            ],
        ),
    ]
