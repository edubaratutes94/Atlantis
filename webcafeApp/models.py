import datetime
import uuid
import os
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class UserApp(User):
    uui = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    image = models.ImageField(upload_to='static/users', verbose_name="Avatar",
                              null=True, default='static/users/userDefault1.png')
    referUser = models.UUIDField(null=True)
    fa2 = models.BooleanField(verbose_name="2FA", default=False)

    def __str__(self):
        return str(self.username)

    def Online(self):
        for s in Session.objects.all():
            if s.get_decoded():
                if self.id == int(s.get_decoded()['_auth_user_id']):
                    now = datetime.datetime.now()
                    dif = (now - s.expire_date)
                    if dif < datetime.timedelta(seconds=0):
                        return True
        return False

    class Meta:
        verbose_name_plural = "Usuarios"


class tipo_producto(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Tipo de Producto",unique=True, null=True)
    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Tipos de Producto"

class Producto(models.Model):
    tipo_producto = models.ForeignKey(tipo_producto, verbose_name="Producto", null=True, on_delete=models.DO_NOTHING)
    descripcion = models.TextField(verbose_name="Descripción", null=True)
    imagen = models.ImageField(upload_to='static/upload', verbose_name="Imagen", null=True)

    def __str__(self):
        return self.tipo_producto.nombre

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Productos"

class tipo_proceso(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Tipo de Proceso",unique=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Tipos de Procesos"

class Proceso(models.Model):
    tipo_proceso = models.ForeignKey(tipo_proceso, verbose_name="Proceso", null=True,on_delete=models.DO_NOTHING)
    descripcion = models.TextField(verbose_name="Descripción", null=True)
    imagen = models.ImageField(upload_to='static/upload', verbose_name="Imagen", null=True, blank=True)
    tipo_producto= models.ForeignKey(Producto, blank=True, null=True,on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.tipo_proceso.nombre

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Procesos"

class Contacto(models.Model):
    titulo = models.CharField(max_length=150, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción", null=True)
    imagen = models.ImageField(upload_to='static/upload', verbose_name="Imagen", null=True, blank=True)

class Empresa(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre Empresa")
    resumen = models.TextField(max_length=1550, verbose_name="Resumen")
    descripcion = models.TextField(verbose_name="Descripción", null=True)
    imagen = models.ImageField(upload_to='static/upload', verbose_name="Imagen", null=True, blank=True)
    correo = models.EmailField(max_length=150, verbose_name="Correo Principal")
    correo_1 = models.EmailField(max_length=150, verbose_name="Correo Secundario", blank=True)
    telefono = models.CharField(max_length=15, verbose_name="Teléfono Principal")
    telefono_2 = models.CharField(max_length=15, verbose_name="Teléfono Secundario", blank=True)
    direccion = models.CharField(max_length=100, verbose_name="Dirección")
    facebook = models.URLField(max_length=100, verbose_name="Facebook", blank=True)
    twitter = models.URLField(max_length=100, verbose_name="Twitter", blank=True)
    instagram = models.URLField(max_length=100, verbose_name="Instagram", blank=True)

class Comentario(models.Model):
    fecha = models.DateTimeField(verbose_name="Fecha", auto_now=True)
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    correo = models.EmailField(max_length=255, verbose_name="Correo")
    descripcion = models.TextField(verbose_name="Descripcion")
    contacto = models.ForeignKey(Contacto, verbose_name="Blog",  blank=True, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.fecha) + "  --  " + self.nombre + " -- " + self.descripcion[:50] + "..."


class Galeria (models.Model):
    fecha = models.DateField(verbose_name='Fecha', auto_now=True)
    titulo = models.CharField(max_length=150, verbose_name="Título")
    imagen = models.ImageField(upload_to='static/upload/galeria', verbose_name="Imagen")
    producto= models.ForeignKey(Producto, blank=True, null=True,on_delete=models.DO_NOTHING)



@receiver(pre_delete, sender=Galeria)
def _directorios_delete(sender, instance, using, **kwargs):
    file_path = str(instance.imagen.path)
    if os.path.isfile(file_path):
        os.remove(file_path)
