"""webcafe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.decorators import login_required, permission_required
from notifications import urls as notiURL
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as djangoViews

from webcafeApp import views, forms

urlpatterns = [

    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/login/', views.loguear, name='ce_login'),
    path('login/', views.just_login, name='just_login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register_front, name="register_front"),
    path('register-by-url/<token>', views.register_by_url, name="register_by_url"),
    # path('administration', login_required(views.inicio), name="inicio"),
    path('backend/', login_required(views.inicio), name="inicio"),

    path('administration/grupo/list', login_required(views.group_list), name="group_list"),
    path('administration/grupo/create', login_required(views.group_create), name='group_create'),
    path('administration/grupo/update/<int:pk>',
         permission_required('ProyectoBaseApp.change_group', login_url='ce_login')(forms.GroupUpdate.as_view()),
         name='group_update'),
    path('administration/grupo/delete/<int:pk>/',
         permission_required('ProyectoBaseApp.delete_group', login_url='ce_login')(forms.GroupDelete.as_view()),
         name='group_delete'),
    path('administration/user/list', login_required(views.user_list), name="user_list"),
    path('administration/user/create', login_required(views.user_create), name='user_create'),
    path('administration/user/update/<int:pk>',
         permission_required('CubaExchangeApp.change_user', login_url='ce_login')(forms.UserUpdate.as_view()),
         name='user_update'),
    path('administration/user/delete/<int:pk>/',
         permission_required('CubaExchangeApp.delete_user', login_url='ce_login')(forms.UserDelete.as_view()),
         name='user_delete'),
    path('administration/password/update/<int:pk>/', login_required(views.password_update),
         name='password_update'),

    # USUARIO
    path('user/password/reset/', views.PasswordResetView.as_view(),
         {'post_reset_redirect': '/user/password/reset/done/'}, name='password_reset'),
    path('user/password/reset/done/', djangoViews.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', djangoViews.PasswordResetConfirmView.as_view(),
         {'post_reset_redirect': '/user/reset/done/'}, name='password_reset_confirm'),
    path('user/reset/done/', djangoViews.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('good/count/activated', views.count_activated, name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('user/update/<int:pk>', login_required(forms.UserUpdateAdmin.as_view()), name="profile"),

    # logs del sistema
    path('administration/logs/list', login_required(views.history_list), name="history_list"),
    path('administration/logs/first_list', login_required(views.history_list_300), name="history_list_300"),

    # NOTIFICACIONES
    path('inbox/notifications/', include(notiURL, namespace='notifications')),
    path('notifications/read/<int:action>', login_required(views.notificacion_read), name="notificacion_read"),

    path('notifications/mark_noti_all_read', login_required(views.notification_all_mark_read), name="mark_all_read"),
    path('notifications/mark_noti_offer_all_read', login_required(views.notification_offer_all_mark_read),
         name="mark_offer_all_read"),

    # CAPTCHA
    path('captcha/', include('captcha.urls')),

    # Salva y Reastaura bdd
    path('administration/db/save', views.db_save, name="db_save"),
    path('administration/db/restore/<str:name>)', views.db_restore, name="db_restore"),
    # Gestion del sitio

    # TIPO DE PRODUCTOS
    path('nomenclador/tipo_producto/list', login_required(views.backend_tipoProducto_listar),
         name="tipo_producto_listar"),
    path('nomenclador/tipo_producto/create', login_required(views.backend_tipoProducto_agregar),
         name="tipo_producto_create"),
    path('nomenclador/tipo_producto/update/<int:pk>', login_required(forms.Update_tipoProducto.as_view()),
         name="tipo_producto_update"),
    path('nomenclador/tipo_producto/delete/<int:pk>', login_required(forms.Delete_tipoProducto.as_view()),
         name="tipo_producto_delete"),
    # Productos
    path('gestion/producto/list', login_required(views.backend_producto_listar), name="producto_listar"),
    path('gestion/producto/create', login_required(views.backend_producto_agregar), name="producto_create"),
    path('gestion/producto/update/<int:pk>', login_required(forms.Update_Producto.as_view()), name="producto_update"),
    path('gestion/producto/delete/<int:pk>', login_required(forms.Delete_Producto.as_view()), name="producto_delete"),

    # Tipo de PROCESOS
    path('nomenclador/tipo_proceso/list', login_required(views.backend_tipoProceso_listar),
         name="tipo_proceso_listar"),
    path('nomenclador/tipo_proceso/create', login_required(views.backend_tipoProceso_agregar),
         name="tipo_proceso_create"),
    path('nomenclador/tipo_proceso/update/<int:pk>', login_required(forms.Update_tipoProceso.as_view()),
         name="tipo_proceso_update"),
    path('nomenclador/tipo_proceso/delete/<int:pk>', login_required(forms.Delete_tipoProceso.as_view()),
         name="tipo_proceso_delete"),

    # Productos
    path('gestion/proceso/list', login_required(views.backend_proceso_listar), name="proceso_listar"),
    path('gestion/proceso/create', login_required(views.backend_proceso_agregar), name="proceso_create"),
    path('gestion/proceso/update/<int:pk>', login_required(forms.Update_Proceso.as_view()), name="proceso_update"),
    path('gestion/proceso/delete/<int:pk>', login_required(forms.Delete_Proceso.as_view()), name="proceso_delete"),

    ### Comentario listar
    path('gestion/comentario/list', login_required(views.backend_comentarios_listar),
         name="comentario_listar"),
    path('gestion/comentario/delete/<int:pk>', login_required(forms.Delete_Comentario.as_view()), name="comentario_delete"),

    #### CONTACTOS
    path('gestion/contacto/list', login_required(views.backend_contactos_listar), name="contacto_listar"),
    path('gestion/contacto/create', login_required(views.backend_contacto_agregar), name="contacto_create"),
    path('gestion/contacto/update/<int:pk>', login_required(forms.Update_Contactos.as_view()), name="contacto_update"),
    path('gestion/contacto/delete/<int:pk>', login_required(forms.Delete_Contactos.as_view()), name="contacto_delete"),

#### EMPRESA
    path('gestion/empresa/list', login_required(views.backend_empresa_listar), name="empresa_listar"),
    path('gestion/empresa/create', login_required(views.backend_empresa_agregar), name="empresa_create"),
    path('gestion/empresa/update/<int:pk>', login_required(forms.Update_Empresa.as_view()), name="empresa__update"),
    path('gestion/empresa/delete/<int:pk>', login_required(forms.Delete_Empresa.as_view()), name="empresa__delete"),

#### Frontend
    path('', views.home, name="home"),
    path('productos/', views.productos_listar.as_view(), name="productos"),
    path('productos/detalle/<int:pk>/', views.detalle_de_producto, name="detalle_de_producto"),
    path('procesos/', views.procesos_listar.as_view(), name="procesos"),
    path('procesos/detalle/<int:pk>/', views.detalle_de_proceso, name="detalle_de_proceso"),
    path('quienes_somos/', views.quienes_somos, name="quienes_somos"),
    path('contactos/', views.contacto, name="contactos"),

]
