"""
URL configuration for djangocrud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from tasks import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('create/tasks/', views.create_task, name='create_task'),
    path('admin/', views.admin, name='solo_admin'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('solicitar_prestamo/', views.solicitar_prestamo, name='solicitar_prestamo'),
    path('mis_prestamos/', views.mis_prestamos, name='mis_prestamos'),
    path('devolver_prestamo/<int:prestamo_id>/', views.devolver_prestamo, name='devolver_prestamo'),
    path('categorias/', views.categorias_disponibles, name='categorias'),
    path('categorias/<str:categoria_slug>/', views.libros_por_categoria, name='libros_por_categoria'),
    path('cambiar_rol_usuario/', views.lista_usuarios, name='lista_usuarios'),
    path('cambiar_rol_usuario/<int:usuario_id>/', views.cambiar_rol_usuario, name='cambiar_rol_usuario'),
    path('autores/', views.lista_autores, name='lista_autores'),
    path('autores/<str:nombre_autor>/', views.libros_por_autor, name='libros_por_autor'),
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('contacto/', views.contacto, name='contacto'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


