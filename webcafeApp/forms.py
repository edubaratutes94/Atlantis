from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.contrib.auth.models import Group,User
from django.views.generic import UpdateView
from django.views.generic.edit import BaseUpdateView, DeleteView
from notifications.signals import notify
from PIL import Image
from captcha.fields import CaptchaField
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets, TextInput, Textarea, EmailInput
from django.http import HttpResponseRedirect

from webcafeApp import models
from webcafeApp.utils import register_logs

class SignUpForm(UserCreationForm):
    captcha = CaptchaField()
    email = forms.EmailField(max_length=254)

    class Meta:
        model = models.UserApp
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Usuario'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'Correo'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Su Nombre'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Sus Apellidos'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Contraseña'
        self.fields['password1'].widget.attrs['minlength'] = '8'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Repita la Contraseña'
        self.fields['password2'].widget.attrs['minlength'] = '8'
        self.fields['captcha'].widget.attrs['class'] = 'form-control'
        self.fields['captcha'].widget.attrs['placeholder'] = 'Captcha'

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            if len(str(email).split("gmail")) > 1:
                if len(str(email).split("+")) > 1:
                    part = str(email).split("@")
                    if len(part) > 1:
                        email = str(part[0]).split("+")[0] + str(part[1])
            match = models.UserApp.objects.get(email=email)
        except models.UserApp.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('Este email ya esta en uso.')

    def clean_username(self):
        # Get the email
        usernam = self.cleaned_data.get('username')

        # Check to see if any users already exist with this email as a username.
        try:
            match = models.UserApp.objects.get(username=usernam)
        except models.UserApp.DoesNotExist:
            # Unable to find a user, this is fine
            return usernam

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('Este nombre de usuario ya esta en uso')


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"
        widgets = {
            "name": widgets.TextInput(attrs={'class': ' form-control'}),
            "permissions": widgets.SelectMultiple(attrs={'class': ' form-control', 'placeholder': 'Rol',
                                                         'style': 'height: 400px'}),
        }


class GroupUpdate(UpdateView):
    form_class = GroupForm
    model = Group
    success_url = reverse_lazy('group_list')

    def post(self, request, *args, **kwargs):
        register_logs(request, Group, self.get_object().pk, self.get_object().__str__(), 2)
        self.object = self.get_object()
        messages.success(request, "Rol modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)


class GroupDelete(DeleteView):
    model = Group
    success_url = reverse_lazy('group_list')

    def delete(self, request, *args, **kwargs):
        register_logs(request, Group, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Rol eliminado con éxito")
        return HttpResponseRedirect(success_url)


class UserForm(UserCreationForm):
    captcha = CaptchaField()
    class Meta:
        model = models.UserApp
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
        widgets = {
            "username": widgets.TextInput(attrs={'class': ' form-control'}),
            "first_name": widgets.TextInput(attrs={'class': ' form-control'}),
            "last_name": widgets.TextInput(attrs={'class': ' form-control'}),
            "email": widgets.EmailInput(attrs={'class': ' form-control'}),
            "password1": widgets.PasswordInput(attrs={'class': ' form-control'}),
            "password2": widgets.PasswordInput(attrs={'class': ' form-control'}),
        }

class UserProfile(forms.ModelForm):
    class Meta:
        model = models.UserApp
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'image',
        ]
        widgets = {
            "username": widgets.TextInput(attrs={'class': ' form-control'}),
            "first_name": widgets.TextInput(attrs={'class': ' form-control','required':'required'}),
            "last_name": widgets.TextInput(attrs={'class': ' form-control','required':'required'}),
            "email": widgets.EmailInput(attrs={'class': ' form-control'}),
            "image": widgets.ClearableFileInput(attrs={'class': ' form-control'}),
        }

class UserAdminProfile(forms.ModelForm):
    class Meta:
        model = models.UserApp
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'groups',
            'is_active',
            'image',
        ]
        widgets = {
            "username": widgets.TextInput(attrs={'class': ' form-control'}),
            "first_name": widgets.TextInput(attrs={'class': ' form-control','required':'required'}),
            "last_name": widgets.TextInput(attrs={'class': ' form-control','required':'required'}),
            "email": widgets.EmailInput(attrs={'class': ' form-control'}),
            "groups": widgets.SelectMultiple(attrs={'class': ' form-control'}),
            "is_active": widgets.CheckboxInput(attrs={'class': ' form-control'}),
            "image": widgets.ClearableFileInput(attrs={'class': ' form-control'}),
        }

class UserUpdateAdmin(UpdateView):
    model = models.UserApp
    form_class = UserProfile
    template_name = ('auth/profile.html')
    success_url = reverse_lazy('inicio')

    def get(self, request, *args, **kwargs):
        if request.user.pk == self.get_object().pk:
            self.object = self.get_object()
            return super(BaseUpdateView, self).get(request, *args, **kwargs)
        else:
            return render(request,'Security/404.html')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.UserApp, self.get_object().uui, self.get_object().__str__(), 2)
        notify.send(request.user, recipient=self.get_object(), verb='Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Usuario modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            if self.request.POST.get('x') != "":
                x = float(self.request.POST.get('x'))
                y = float(self.request.POST.get('y'))
                w = float(self.request.POST.get('width'))
                h = float(self.request.POST.get('height'))

                image = Image.open(self.get_object().image)
                cropped_image = image.crop((x, y, w + x, h + y))
                resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
                resized_image.save(self.get_object().image.path)
            url = force_text(self.success_url)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

class UserUpdate(UpdateView):
    model = models.UserApp
    form_class = UserAdminProfile
    template_name = ('auth/user_form.html')
    success_url = reverse_lazy('user_list')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.UserApp, self.get_object().uui, self.get_object().__str__(), 2)
        notify.send(request.user, recipient=self.get_object(), verb='Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Usuario modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

class UserDelete(DeleteView):
    model = User
    success_url = reverse_lazy('user_list')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.UserApp, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Usuario eliminado con éxito")
        return HttpResponseRedirect(success_url)




## Tipo de Producto

class Form_tipoProducto(forms.ModelForm):
    class Meta:
        model = models.tipo_producto
        fields = [
            'nombre',

        ]
        widgets = {
            "nombre": widgets.TextInput(attrs={'class': ' form-control', 'required': 'required'}),

        }


class Update_tipoProducto(UpdateView):
    model = models.tipo_producto
    form_class = Form_tipoProducto
    template_name = ('webcafeApp/tipo_producto_form.html')
    success_url = reverse_lazy('tipo_producto_listar')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.tipo_producto, self.get_object().pk, self.get_object().__str__(), 2)
        # notify.send(request,'Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Tipo de Producto modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

class Delete_tipoProducto(DeleteView):
    model = models.tipo_producto
    success_url = reverse_lazy('tipo_producto_listar')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.tipo_producto, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Tipo de Producto eliminado con éxito")
        return HttpResponseRedirect(success_url)

# FORM PRODUCTO

class Form_Producto(forms.ModelForm):
    class Meta:
        model = models.Producto
        fields = [
            'tipo_producto',
            'descripcion',
            'imagen',

        ]
        widgets = {
            "tipo_producto": widgets.Select(attrs={'class': ' form-control', 'required': 'required'}),
            "descripcion": widgets.Textarea(attrs={'class': ' form-control', 'required': 'required'}),
            # "email": widgets.EmailInput(attrs={'class': ' form-control'}),
            # "groups": widgets.SelectMultiple(attrs={'class': ' form-control'}),
            # "is_active": widgets.CheckboxInput(attrs={'class': ' form-control'}),
            # "imagen": widgets.FileInput(attrs={'class': ' form-control'}),
        }

class Update_Producto(UpdateView):
    model = models.Producto
    form_class = Form_Producto
    template_name = ('webcafeApp/producto_form.html')
    success_url = reverse_lazy('producto_listar')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.Producto, self.get_object().pk, self.get_object().__str__(), 2)
        # notify.send(request.user , recipient=self.get_object(), verb='Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Producto modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

class Delete_Producto(DeleteView):
    model = models.Producto
    success_url = reverse_lazy('producto_listar')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.Producto, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Producto eliminado con éxito")
        return HttpResponseRedirect(success_url)

## TIPO DE PROCESO

class Form_tipoProceso(forms.ModelForm):
    class Meta:
        model = models.tipo_proceso
        fields = [
            'nombre',

        ]
        widgets = {
            "nombre": widgets.TextInput(attrs={'class': ' form-control', 'required': 'required'}),

        }

class Update_tipoProceso(UpdateView):
    model = models.tipo_proceso
    form_class = Form_tipoProceso
    template_name = ('webcafeApp/tipo_proceso_form.html')
    success_url = reverse_lazy('tipo_proceso_listar')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.tipo_proceso, self.get_object().pk, self.get_object().__str__(), 2)
        # notify.send(request,'Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Tipo de Proceso modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

class Delete_tipoProceso(DeleteView):
    model = models.tipo_proceso
    success_url = reverse_lazy('tipo_proceso_listar')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.tipo_proceso, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Tipo de Proceso eliminado con éxito")
        return HttpResponseRedirect(success_url)


# FORM PROCESO

class Form_Proceso(forms.ModelForm):
    class Meta:
        model = models.Proceso
        fields = [
            'tipo_proceso',
            'tipo_producto',
            'descripcion',
            'imagen',

        ]
        widgets = {
            "tipo_proceso": widgets.Select(attrs={'class': ' form-control', 'required': 'required'}),
            "tipo_producto": widgets.Select(attrs={'class': ' form-control', 'required': 'required'}),
            "descripcion": widgets.Textarea(attrs={'class': ' form-control', 'required': 'required'}),
            # "imagen": widgets.FileInput(attrs={'class': ' form-control'}),
        }

class Update_Proceso(UpdateView):
    model = models.Proceso
    form_class = Form_Proceso
    template_name = ('webcafeApp/proceso_form.html')
    success_url = reverse_lazy('proceso_listar')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.Proceso, self.get_object().pk, self.get_object().__str__(), 2)
        # notify.send(request.user , recipient=self.get_object(), verb='Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Proceso modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

class Delete_Proceso(DeleteView):
    model = models.Proceso
    success_url = reverse_lazy('proceso_listar')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.Proceso, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Proceso eliminado con éxito")
        return HttpResponseRedirect(success_url)

## Contactos

class Form_Contactos(forms.ModelForm):
    class Meta:
        model = models.Contacto
        fields = [
            'titulo',
            'descripcion',
            'imagen',

        ]
        widgets = {
            "titulo": widgets.TextInput(attrs={'class': ' form-control', 'required': 'required'}),
            "descripcion": widgets.Textarea(attrs={'class': ' form-control', 'required': 'required'}),
            # "email": widgets.EmailInput(attrs={'class': ' form-control'}),
            # "groups": widgets.SelectMultiple(attrs={'class': ' form-control'}),
            # "is_active": widgets.CheckboxInput(attrs={'class': ' form-control'}),
            # "imagen": widgets.FileInput(attrs={'class': ' form-control'}),
        }

class Update_Contactos(UpdateView):
    model = models.Contacto
    form_class = Form_Contactos
    template_name = ('webcafeApp/contacto_form.html')
    success_url = reverse_lazy('contacto_listar')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.Contacto, self.get_object().pk, self.get_object().__str__(), 2)
        # notify.send(request.user , recipient=self.get_object(), verb='Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Contacto modificado con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

class Delete_Contactos(DeleteView):
    model = models.Contacto
    success_url = reverse_lazy('contacto_listar')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.Contacto, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Contacto eliminado con éxito")
        return HttpResponseRedirect(success_url)


## QUIENES SOMOS

class Form_Empresa(forms.ModelForm):
    class Meta:
        model = models.Empresa
        fields = [
            'nombre',
            'resumen',
            'descripcion',
            'imagen',
            'correo',
            'correo_1',
            'telefono',
            'telefono_2',
            'direccion',
            'facebook',
            'twitter',
            'instagram',

        ]
        widgets = {
            "nombre": widgets.TextInput(attrs={'class': ' form-control', 'required': 'required'}),
            "resumen": widgets.Textarea(attrs={'class': ' form-control', 'required': 'required'}),
            "descripcion": widgets.Textarea(attrs={'class': ' form-control', 'required': 'required'}),
            "correo": widgets.EmailInput(attrs={'class': ' form-control'}),
            "correo_1": widgets.EmailInput(attrs={'class': ' form-control'}),
            "telefono": widgets.TextInput(attrs={'class': ' form-control' ,'required': 'required'}),
            "telefono_2": widgets.TextInput(attrs={'class': ' form-control'}),
            "direccion": widgets.TextInput(attrs={'class': ' form-control'}),
            "facebook": widgets.TextInput(attrs={'class': ' form-control'}),
            "twitter": widgets.TextInput(attrs={'class': ' form-control'}),
            "instagram": widgets.TextInput(attrs={'class': ' form-control'}),
        }

class Update_Empresa(UpdateView):
    model = models.Empresa
    form_class = Form_Empresa
    template_name = ('webcafeApp/empresa_form.html')
    success_url = reverse_lazy('empresa_listar')

    def post(self, request, *args, **kwargs):
        register_logs(request, models.Empresa, self.get_object().pk, self.get_object().__str__(), 2)
        # notify.send(request.user , recipient=self.get_object(), verb='Se han modificado sus datos', level='warning')
        self.object = self.get_object()
        messages.success(request, "Empresa modificada con éxito")
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

class Delete_Empresa(DeleteView):
    model = models.Empresa
    success_url = reverse_lazy('empresa_listar')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.Empresa, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Empresa eliminado con éxito")
        return HttpResponseRedirect(success_url)


class ComentarioForm(forms.Form):
    nombre = forms.CharField(label="Nombre", required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Nombre', 'autocomplete': 'off'}))
    correo = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email', 'autocomplete': 'off'}))
    mensaje = forms.CharField(label="Mensaje", required=True, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Mensaje', 'autocomplete': 'off'}))

class Delete_Comentario(DeleteView):
    model = models.Comentario
    success_url = reverse_lazy('comentario_listar')

    def delete(self, request, *args, **kwargs):
        register_logs(request, models.Comentario, self.get_object().pk, self.get_object().__str__(), 3)
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Comentario eliminado con éxito")
        return HttpResponseRedirect(success_url)



