 # coding=utf-8

import json
import re
from django.contrib import messages
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_str
from django.views.generic import View




class RequiredSecurityMixin(object):
    """
       @Desc: Comprueba que el usuario este autenticado y que tenga los permisos para acceder a la vista.
       """
    # Code name list
    CREATE = 'add'
    CHANGE = 'change'
    DELETE = 'delete'
    LIST = 'list'

    need_login = False
    permission = None

    def dispatch(self, request, *args, **kwargs):
        if self.need_login and self.permission:
            @login_required
            @permission_required(
                '%s.%s_%s' % (self.model._meta.app_label, self.permission, self.model._meta.model_name),
                raise_exception=True)
            def wrapper(request, *args, **kwargs):
                return super(RequiredSecurityMixin, self).dispatch(request, *args, **kwargs)
        elif self.need_login and not self.permission:
            @login_required
            def wrapper(request, *args, **kwargs):
                return super(RequiredSecurityMixin, self).dispatch(request, *args, **kwargs)
        else:
            def wrapper(request, *args, **kwargs):
                return super(RequiredSecurityMixin, self).dispatch(request, *args, **kwargs)

        return wrapper(request, *args, **kwargs)


class BaseDeleteView(SuccessMessageMixin, View):
    """
    @Desc: Vista genérica para la eliminación de objetos
    """

    def get(self, request, *args, **kwargs):
        obj = self.model.objects.get(pk=kwargs['pk'])
        obj.delete()
        register_logs(request, self.model, kwargs['pk'], force_str(obj), DELETION)
        messages.success(self.request, self.success_message.replace('objeto', force_str(obj)))
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        pk_list = json.loads(request.POST.get('items'))
        for item in pk_list:
            obj = self.model.objects.get(pk=item)
            obj.delete()
            register_logs(request, self.model, item, force_str(obj), DELETION)
        messages.success(self.request, 'Se eliminaron satisfactoriamente todos los elementos.')
        return HttpResponseRedirect(self.get_success_url())


def get_client_ip(request):
    x_forwarded_for = request.META.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def register_logs(request, model, object_id, object_unicode, action):
    """
    @Desc: Funcion utilizada para registrar los logs de las acciones generadas por el usuario
    """
    if request.user.pk:
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(model).pk,
            object_id=object_id,
            object_repr=object_unicode,
            change_message=get_client_ip(request),
            # action flag es 0 listar,1 agregar,2 modificar,3 eliminar,4 entrar, 5 salir, 6 activar, 7 desactivar, 8 reactivar, 9 Error User Password, 10 user login apk, 11 Base de datos
            action_flag=action
        )
    else:
        LogEntry.objects.log_action(
            user_id=1,
            content_type_id=ContentType.objects.get_for_model(model).pk,
            object_id=object_id,
            object_repr=object_unicode,
            change_message=get_client_ip(request),
            # action flag es 0 listar,1 agregar,2 modificar,3 eliminar,4 entrar, 5 salir, 6 activar, 7 desactivar, 8 reactivar, 9 Error User Password, 10 user login apk, 11 base de datos
            action_flag=action
        )


def menu_builder(request):
    """
    @Desc: Procesador de contexto usado para poblar el menu en cada peticion.
    """
    navigation = {'menu': [
        {'name': 'Inicio', 'url': reverse('home'), 'icon': True, 'icon_class': 'icon-home'},
        {'name': 'Captura Datos', 'url': reverse('persona')},
    ]}

    for item in navigation['menu']:
        if item['url'] in request.path:
            item['active'] = True

    return navigation


def validate_only_letters(value):
    """
    @Desc: Funcion para validar entrada de solo letras
    """
    p = re.compile(u"[a-zA-ZñÑáéíóú ]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Solo se admiten letras.')


def validate_correo(value):
    msg_error = []
    aux = str(value).split("@")
    if aux.__len__() == 2:
        name = aux[0]
        domine = aux[1]
        if name == "":
            msg_error.append("EL correo debe tener una cadena de caracteres antes de @")
        if not domine.split(".")[0]:
            msg_error.append("Error en el dominio en la dirección de correo")
    else:
        msg_error.append("EL correo debe tener el caracter @")
    return msg_error

def validate_only_letters_may(value):
    """
    @Desc: Funcion para validar entrada con mayuscula
    """
    p = re.compile(u"[A-Z]{1}[a-z]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Debe empezar con mayúscula.')
def validate_only_may_letter(value):
    """
    @Desc: Funcion para validar entrada solo con mayusculas
    """
    p = re.compile(u"[A-Z]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'solo mayúsculas')


def validate_only_letters_plus(value):
    """
    @Desc: Funcion para validar entrada de solo letras
    """
    p = re.compile(u"[a-zA-ZñÑáéíóú +-]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Solo se admiten letras.')


def validate_only_letters_min(value):
    """
    @Desc: Funcion para validar entrada de solo letras minúsculas
    """
    p = re.compile(u"[a-z]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Solo se admite letras minúscula.')


def validate_only_numbers(value):
    """
    @Desc: Funcion para validar entrada de solo números
    """
    array = str(value).split(".")
    p = re.compile(u"[0-9]+$")
    if array.__len__()>1:
        m = p.match(array[0])
        n = p.match(array[1])
        if not m or not n:
            raise ValidationError(u'Solo se admiten números.')
    elif array.__len__()==1:
        m = p.match(array[0])
        if not m:
            raise ValidationError(u'Solo se admiten números.')


def validate_only_numbers_carne(value):
    """
    @Desc: Funcion para validar entrada de solo 11 dígitos en el carné de identidad del empleado.
    """
    p = re.compile(u"\d+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Solo se admiten números.')
    if value.__len__() != 11:
        raise ValidationError(u'El carné de identidad debe contener 11 dígitos.')


def validate_only_letters_numbers(value):
    """
    @Desc: Funcion para validar entrada de solo letras y números
    """
    p = re.compile(u"[a-zA-ZñÑáéíóú0-9 ]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Solo se admiten letras y números.')


def validate_only_letters_numbers_plus(value):
    """
    @Desc: Funcion para validar entrada de solo letras y números
    """
    p = re.compile(u"[a-zA-ZñÑáéíóú0-9 +-]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Solo se admiten letras y números.')


def validate_tcelular(value):
    """
    @Desc: Funcion para validar número de solapin válido
    """
    p = re.compile(u"[5][0-9]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'El número de teléfono presenta errores. Ej:(5...).')
    if value.__len__() != 8:
        raise ValidationError(u'Error en la cantidad de cifras.')


def validate_tfijo(value):
    """
    @Desc: Funcion para validar número de solapin válido
    """
    p = re.compile(u"[7][0-9]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'El número de teléfono presenta errores. Ej:(7...).')
    if value.__len__() != 8:
        raise ValidationError(u'Error en la cantidad de cifras.')


def validate_carne(value):
    """
    @Desc: Funcion para validar entrada de solo 11 dígitos en el carné de identidad del empleado.
    """
    p = re.compile(u"\d+$")
    a = re.compile(u"([0-9]{2})(0?[1-9]|1[012])(0?[1-9]|[12][0-9]|3[01])([0-9]{5})$")
    m = p.match(value)
    l = a.match(value)

    # validar mes con dias
    mes = str(value[2:4])
    dia = str(value[4:6])
    error_dia = ""
    error_mes = ""


    if mes == "01" or mes == "03" or mes == "05" or mes == "07" or mes == "08" or mes == "10" or mes == "12":
        if int(dia) > 31 or int(dia) < 1:
            error_dia = "Tiene error en el dia del carne"
    else:
        if mes == '02':
            if int(dia)>29 or int(dia)<1:
                error_dia = "Recuerde que febrero tiene solo 28-29 días, arregle el carne"
        else:
            if int(dia)>31 or int(dia)<1:
                error_dia = "Error en el dia en el carne"
    if not m:
        raise ValidationError(u'Solo se admiten números.')
    if not l:
        raise ValidationError(u'Esta incorrecta la estructura del carnet de identidad.')
    if value.__len__() != 11:
        raise ValidationError(u'El carné de identidad debe contener 11 dígitos.')
    if error_dia != "":
        raise ValidationError(error_dia)
    if error_mes != "":
        raise ValidationError(error_mes)


def validate_nombre(value):
    """
    @Desc: Funcion para validar entrada de solo apellidos
    """
    p = re.compile(u"[A-Z]{1}[a-zñáéíóú]*(\s*[A-Z]{1}[a-zñáéíóú]*)$")
    v = re.compile(u"[A-Z]{1}[a-zñáéíóú]+$")

    m = p.match(value)
    i = v.match(value)
    if not i:
        if not m:
            raise ValidationError(u'Error, nombre incorrecto.')


def validate_apellidos(value):
    """
    @Desc: Funcion para validar entrada de solo apellidos
    """
    p = re.compile("[A-Z]{1}[a-zñáéíóú]+(\s*[A-Z]{1}[a-zñáéíóú]*)$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Debe entrar correctamente los dos apellidos.')


def validate_fecha(value):
    """
    @Desc: Funcion para validar número de solapin válido
    """
    p = re.compile(u"(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d)+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Número de solapin inválido.')


def validate_direccion(value):
    """
    @Desc: Funcion para validar la direccion
    """
    p = re.compile(u"^\d{1}[ABCEGHJKLMNPRSTVXY]{1}\d{1}[A-Z]{1} *\d{1}[A-Z]{1}\d{1}$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Introduzca una dirección válida.')


def validate_asunto(value):
    """
    @Desc: Funcion para validar entrada de solo apellidos
    """
    p = re.compile(u"[A-Z]{1}[a-zñáéíóú]*[a-z-ñáéíóú ]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Asunto debe comenzar con mayúscula y contener solo letras.')


def validate_register_user(value):
    """
    @Desc: Funcion para validar la entrada del usuario con el formato correcto
    """
    p = re.compile(u"[a-zA-Z0-9@.+-_]+$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Usuario no válido. Solo se admiten 150 caracteres o menos, '
                              u'letras, números y @/./+/-/_ .')


def validate_not_whitespace(value):
    """
    @Desc: Funcion para validar entrada sin espacios en blanco
    """
    p = re.compile(u"[\s]+$")
    m = p.match(value)
    if m:
        raise ValidationError(u'No se admiten espacios solamente.')


def validate_passport_number(value):
    """
    @Desc: Funcion para validar número de pasaporte válido
    """
    p = re.compile(u"[A-Z][0-9]{7}$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Número de pasaporte no válido.')


def validate_cheque(value):
    """
    @Desc: Funcion para validar número de cheque
    """
    p = re.compile(u"[0-9]+(-[0-9]+)*$")
    m = p.match(value)
    if not m:
        raise ValidationError(u'Introduzca un número de cheque válido.')

def delete_address_db(address):
    fich = open(address, "w")
    fich.writelines(["Cleaned"])
    fich.close()

def list_address_db():
    fich = open("static/db/dblist.mytxt")
    lines = fich.readlines()
    fich.close()
    res = []
    if lines.__len__()>0:
        for line in lines:
            fich = line.split("/")[2]
            date = fich.split("_")[0]
            Year = date[0:4]
            Mounth = date[4:6]
            Day = date[6:8]
            res.append([fich,Year,Mounth,Day])
    return res

def save_address_dbs(address):
    fich = open("static/db/dblist.mytxt")
    lines = fich.readlines()
    fich.close()
    address = address + "\n"
    if address not in lines:
        if lines.__len__() == 0:
            lines.append(address)
        if lines.__len__() == 2:
            delete_address_db(lines[1][0:-1])
        if lines.__len__() > 0 or lines.__len__() < 3:
            first = lines[0]
            lines.clear()
            lines.append(address)
            lines.append(first)
    fich = open("static/db/dblist.mytxt", "w")
    fich.writelines(lines)
    fich.close()

