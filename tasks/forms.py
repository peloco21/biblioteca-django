from django import forms
from .models import Libros
from .models import Prestamo
from django.utils import timezone
from django.contrib.auth.models import User
import json

class TaskForm(forms.ModelForm):
    categoria = forms.ChoiceField(
        choices=Libros.CATEGORIAS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_categoria'})
    )

    subcategoria = forms.ChoiceField(
        choices=[('', 'Seleccione una subcategoría')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_subcategoria'})
    )

    sinopsis = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Sinopsis"
    )
    
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label="Descripción"
    )

    portada = forms.ImageField(
        required=False,
        label="Portada"
    )

    class Meta:
        model = Libros
        fields = [
            'titulo', 'autor', 'editorial', 'año', 'isbn', 'ejemplares_disponibles',
            'categoria', 'subcategoria', 'sinopsis', 'num_paginas', 'idioma', 'formato', 'edicion', 'portada',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categoria = None

        # Se intenta obtener la categoría desde los datos enviados o desde los iniciales
        if self.is_bound:
            categoria = self.data.get('categoria')
        else:
            categoria = self.initial.get('categoria')

        if categoria:
            subcategorias = Libros.SUBCATEGORIAS.get(categoria, [])
            self.fields['subcategoria'].choices = [('', 'Seleccione una subcategoría')] + subcategorias
        else:
            self.fields['subcategoria'].choices = [('', 'Seleccione una subcategoría')]

    def clean_subcategoria(self):
        categoria = self.cleaned_data.get('categoria')
        subcategoria = self.cleaned_data.get('subcategoria')

        if subcategoria:
            opciones_validas = dict(Libros.SUBCATEGORIAS.get(categoria, []))
            if subcategoria not in opciones_validas:
                raise forms.ValidationError("La subcategoría no es válida para la categoría seleccionada.")
        return subcategoria

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['libro', 'fecha_devolucion_estimada']

    fecha_devolucion_estimada = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date(),
        label="Fecha de Devolución Estimada"
    )

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class FiltroLibrosForm(forms.Form):
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + Libros.CATEGORIAS,
        required=False,
        label='Categoría'
    )
    titulo = forms.CharField(max_length=100, required=False, label='Título')

