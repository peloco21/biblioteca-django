from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User,  Group
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Libros
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Libros
from .forms import PrestamoForm
from .models import Prestamo
from django.utils import timezone
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from .forms import PerfilUsuarioForm
from datetime import date, timedelta
import json

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput,
        help_text='La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un signo especial.',
        validators=[]  
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].help_text = 'Verifica la contraseña'

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password)
        except ValidationError as e:
            errores_traducidos = []
            for mensaje in e.messages:
                if "This password is too short" in mensaje:
                    errores_traducidos.append("La contraseña es demasiado corta. Debe tener al menos 8 caracteres.")
                elif "This password is too common" in mensaje:
                    errores_traducidos.append("Esta contraseña es demasiado común.")
                elif "This password is entirely numeric" in mensaje:
                    errores_traducidos.append("Esta contraseña es completamente numérica.")
                else:
                    errores_traducidos.append(mensaje)
            raise ValidationError(errores_traducidos)
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def _post_clean(self):

        super(forms.ModelForm, self)._post_clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
            invitado_group, created = Group.objects.get_or_create(name='invitado')
            user.groups.add(invitado_group)
        return user



def admin(request):
    return render(request, 'solo_admin.html')

def home(request):
  return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': CustomUserCreationForm()
        })
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                form.add_error('username', 'Este nombre de usuario ya está en uso.')
        return render(request, 'signup.html', {
            'form': form 
        })

from django.db.models import F

def tasks(request):
    # filtros
    titulo = request.GET.get('titulo', '')
    autor = request.GET.get('autor', '')
    editorial = request.GET.get('editorial', '')
    año = request.GET.get('año', '')
    isbn = request.GET.get('isbn', '')
    categoria = request.GET.get('categoria', '')
    subcategoria = request.GET.get('subcategoria', '')
    letra = request.GET.get('letra', '')

    libros = Libros.objects.all()

    if titulo:
        libros = libros.filter(titulo__icontains=titulo)
    if autor:
        libros = libros.filter(autor__icontains=autor)
    if editorial:
        libros = libros.filter(editorial__icontains=editorial)
    if año:
        libros = libros.filter(año=año)
    if isbn:
        libros = libros.filter(isbn=isbn)
    if categoria:
        libros = libros.filter(categoria=categoria)
    if subcategoria:
        libros = libros.filter(subcategoria=subcategoria)
    if letra:
        libros = libros.filter(titulo__istartswith=letra)

    categorias = Libros.CATEGORIAS 
    subcategorias_json = json.dumps(Libros.SUBCATEGORIAS)  # <-- aquí

    return render(request, 'tasks.html', {
        'tasks': libros,
        'titulo': titulo,
        'autor': autor,
        'editorial': editorial,
        'año': año,
        'isbn': isbn,
        'categoria': categoria,
        'subcategoria': subcategoria,
        'categorias': categorias,
        'subcategorias_json': subcategorias_json,  # <-- y aquí
        'letra': letra,
    })

import json
from .models import Libros
from .forms import TaskForm

def create_task(request):
    if request.method == 'GET':
        form = TaskForm()
        subcategorias_json = json.dumps(Libros.SUBCATEGORIAS)
        return render(request, 'create_task.html', {'form': form, 'subcategorias_json': subcategorias_json})
    else:
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        else:
            subcategorias_json = json.dumps(Libros.SUBCATEGORIAS)
            return render(request, 'create_task.html', {'form': form, 'subcategorias_json': subcategorias_json})

        
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
            'form': AuthenticationForm,
            'error': 'Usuario o contraseña incorrectos'
        })
        else:
            login(request, user)
            return redirect('tasks')
        
def task_detail(request, task_id):
    libro = get_object_or_404(Libros, pk=task_id)
    es_admin = request.user.groups.filter(name='admin').exists()
    es_duenio = libro.user == request.user
    tiene_permiso = es_admin or es_duenio

    subcategorias_json = json.dumps(Libros.SUBCATEGORIAS)

    if request.method == 'GET':
        if not tiene_permiso:
            return render(request, 'task_detail.html', {
                'libro': libro,
                'tiene_permiso': False
            })

        form = TaskForm(instance=libro)
        return render(request, 'task_detail.html', {
            'libro': libro,
            'form': form,
            'tiene_permiso': True,
            'subcategorias_json': subcategorias_json,  # <-- aquí
        })

    else:
        if not tiene_permiso:
            return render(request, 'task_detail.html', {
                'libro': libro,
                'error': 'No tienes permiso para editar este libro.',
                'tiene_permiso': False
            })

        try:
            form = TaskForm(request.POST, request.FILES, instance=libro)
            if form.is_valid():
                form.save()
                return redirect('tasks')
            else:
                return render(request, 'task_detail.html', {
                    'libro': libro,
                    'form': form,
                    'error': 'Formulario inválido',
                    'tiene_permiso': True,
                    'subcategorias_json': subcategorias_json,  # <-- aquí también
                })
        except ValueError:
            return render(request, 'task_detail.html', {
                'libro': libro,
                'form': form,
                'error': 'Error al actualizar el libro.',
                'tiene_permiso': True,
                'subcategorias_json': subcategorias_json,  # <-- aquí también
            })

        
def delete_task(request, task_id):
    libro = get_object_or_404(Libros, pk=task_id)

    if libro.user != request.user and not request.user.groups.filter(name='admin').exists():
        return redirect('tasks')

    libro.delete()
    return redirect('tasks')

from .forms import FiltroLibrosForm
from django.contrib import messages
def solicitar_prestamo(request):
    categorias = Libros.CATEGORIAS
    selected_categoria = request.GET.get('categoria', '')
    selected_titulo = request.GET.get('titulo', '')

    libros = Libros.objects.all()
    if selected_categoria:
        libros = libros.filter(categoria=selected_categoria)
    if selected_titulo:
        libros = libros.filter(titulo__icontains=selected_titulo)

    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        form.fields['libro'].queryset = libros 

        if form.is_valid():
            prestamos_activos = Prestamo.objects.filter(
                usuario=request.user,
                estado__in=['pendiente', 'en_retraso']
            ).count()

            if prestamos_activos >= 5:
                messages.error(request, "No puedes solicitar más de 5 préstamos activos. Devuelve alguno antes de pedir otro.")
            else:
                prestamo = form.save(commit=False)
                prestamo.usuario = request.user
                prestamo.save()
                messages.success(request, "Préstamo solicitado con éxito.")
                return redirect('mis_prestamos')
    else:
        form = PrestamoForm()
        form.fields['libro'].queryset = libros

    context = {
        'form': form,
        'categorias': categorias,
        'selected_categoria': selected_categoria,
        'selected_titulo': selected_titulo,
    }
    return render(request, 'solicitar_prestamo.html', context)

def mis_prestamos(request):
    prestamos = Prestamo.objects.filter(usuario_id=request.user.id)
    fecha_actual = timezone.now().date()
    prestamos_con_estado = []

    for prestamo in prestamos:
        esta_retrasado = False
        if prestamo.estado == 'pendiente' and prestamo.fecha_devolucion_estimada < fecha_actual:
            esta_retrasado = True
        prestamos_con_estado.append({
            'prestamo': prestamo,
            'retrasado': esta_retrasado,
        })

    return render(request, 'mis_prestamos.html', {'prestamos_con_estado': prestamos_con_estado})

def devolver_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id, usuario=request.user)

    if request.method == 'POST':
        if prestamo.estado == 'pendiente':
            prestamo.fecha_devolucion_real = timezone.now()
            prestamo.estado = 'devuelto'
            prestamo.save()
        return redirect('mis_prestamos')

    return render(request, 'devolver_prestamos.html', {'prestamo': prestamo})

def crear_prestamo(request, libro_id):
    libro = get_object_or_404(Libros, id=libro_id)
    
  
    prestamo = Prestamo(
        usuario=request.user,
        libro=libro,
        fecha_prestamo=timezone.now(),
        fecha_devolucion_estimada=request.POST.get('fecha_devolucion_estimada'),
        estado='Pendiente',  
    )
    prestamo.save()

    return redirect('mis_prestamos')


def categorias_disponibles(request):
    categorias = dict(Libros.CATEGORIAS)
    categoria = request.GET.get('categoria', '')

    if categoria:
        libros = Libros.objects.filter(categoria=categoria)
    else:
        libros = Libros.objects.all()

    return render(request, 'categorias.html', {
        'categorias': categorias,
        'categoria': categoria,
        'libros': libros,
    })


def contacto(request):
    return render(request, 'contacto.html')


def libros_por_categoria(request, categoria_slug):
    libros = Libros.objects.filter(categoria=categoria_slug)
    return render(request, 'libros_por_categoria.html', {
        'libros': libros,
        'categoria': dict(Libros.CATEGORIAS).get(categoria_slug, categoria_slug)
    })

def cambiar_rol_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')

      
        usuario.groups.clear()

        group, created = Group.objects.get_or_create(name=nuevo_rol)
        usuario.groups.add(group)

        
        if nuevo_rol == 'admin':
            usuario.is_superuser = True
        else:
            usuario.is_superuser = False  

        usuario.save()
        return redirect('lista_usuarios')  
    
    return render(request, 'cambiar_rol_usuario.html', {'usuario': usuario})

def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})


import string
def lista_autores(request):
    query = request.GET.get('q', '')
    inicial = request.GET.get('inicial', '')

    autores_qs = Libros.objects.values('autor').annotate(total=Count('id')).order_by('autor')

    if query:
        autores_qs = autores_qs.filter(autor__icontains=query)
    if inicial:
        autores_qs = autores_qs.filter(autor__istartswith=inicial)

    letras_con_autores = set(Libros.objects.values_list('autor', flat=True)
                             .exclude(autor__isnull=True)
                             .exclude(autor__exact='')
                             .annotate()[::1])
    letras_activas = {a[0].upper() for a in letras_con_autores}

    abecedario = list(string.ascii_uppercase)

    return render(request, 'lista_autores.html', {
        'autores': autores_qs,
        'query': query,
        'inicial': inicial,
        'letras': abecedario,
        'letras_activas': letras_activas,
    })

def libros_por_autor(request, nombre_autor):
    libros = Libros.objects.filter(autor=nombre_autor)
    return render(request, 'libros_por_autor.html', {'libros': libros, 'autor': nombre_autor})

def ver_perfil(request):
    if request.method == 'POST':
        user_form = PerfilUsuarioForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            return redirect('home')

    else:
        user_form = PerfilUsuarioForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'perfil.html', {
        'user_form': user_form,
        'password_form': password_form,
    })

