from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms


class Libros(models.Model):
    CATEGORIAS = [
        ('romance', 'Romantica'),
        ('accion', 'Acción'),
        ('aventura', 'Aventura'),
        ('ciencia', 'Ciencia Ficción'),
        ('terror', 'Terror'),
        ('drama', 'Drama'),
        ('comedia', 'Comedia'),
        ('fantasia', 'Fantasía'),
        ('historia', 'Histórica'),
        ('biografia y autobiografia', 'Biografía y Autobiografía'),
        ('misterio', 'Misterio'),
        ('poesia', 'Poesía'),
        ('educativo', 'Educativo'),
        ('infantil', 'Infantil'),
        ('belica', 'Bélica'),
        ('juvenil', 'Juvenil'),
        ('saga', 'Saga'),  
    ]

    SUBCATEGORIAS = {
        'romance': [
            ('contemporanea', 'Contemporánea'),
            ('erotica', 'Erótica'),
            ('historica', 'Histórica'),
        ],
        'accion': [
            ('espionaje', 'Espionaje'),
            ('militar', 'Militar'),
            ('crimen', 'Crimen Organizado'),
        ],
        'terror': [
            ('psicologico', 'Psicológico'),
            ('sobrenatural', 'Sobrenatural'),
            ('slasher', 'Slasher'),
        ],
        'drama': [
            ('familiar', 'Familiar'),
            ('social', 'Social'),
            ('romantico', 'Romántico'),
        ],
        'comedia': [
            ('romantica', 'Romántica'),
            ('satira', 'Sátira'),
            ('negra', 'Negra'),
        ],
        'fantasia': [
            ('epica', 'Épica'),
            ('urbana', 'Histórica'),
            ('oscura', 'Oscura'),
        ],
        'historia': [
            ('antigua', 'Antigua'),
            ('contemporanea', 'Contemporánea'),
            ('biografica', 'Biográfica'),
        ],
        'biografia y autobiografia': [
            ('biografia', 'Biografia'),
            ('autobiografia', 'Autobiografia'),
        ],
        'misterio': [
            ('detectivesco', 'Detectivesco'),
            ('psicologico', 'Psicológico'),
            ('thriller', 'Thriller'),
        ],
        'poesia': [
            ('amor', 'de Amor'),
            ('existencial', 'Existencial'),
            ('narrativa', 'Narrativa'),
        ],
        'educativo': [
            ('manual', 'Manual'),
            ('ensayo', 'Ensayo'),
            ('guia', 'Guía Didáctica'),
        ],
        'infantil': [
            ('cuento', 'Cuentos'),
            ('didactico', 'Didáctico'),
            ('aventura', 'de Aventura'),
        ],
        'belica': [
            ('primera_guerra', 'Primera Guerra Mundial'),
            ('segunda_guerra', 'Segunda Guerra Mundial'),
            ('estrategia', 'Estrategica'),
            ('testimonio', 'de Testimonio'),
        ],
        'juvenil': [
            ('romantica', 'Romántica'),
            ('fantastica', 'de Fantasía'),
            ('fanfic', 'Fanfic'),
        ],
        'saga': [
            ('fantasia', 'de Fantasía'),
            ('ciencia_ficcion', 'de Ciencia Ficción'),
            ('aventura', 'de Aventura'),
            ('romantica', 'Romántica'),
        ],
    }

    IDIOMAS = [
        ('es', 'Español'),
        ('en', 'Inglés'),
        ('fr', 'Francés'),
        ('de', 'Alemán'),
        ('it', 'Italiano'),
        ('pt', 'Portugués'),
    ]

    FORMATOS = [
        ('tapa_blanda', 'Tapa blanda'),
        ('tapa_dura', 'Tapa dura'),
        ('audiolibro', 'Audiolibro'),
    ]

    EDICIONES = [
        ('primera', 'Primera'),
        ('segunda', 'Segunda'),
        ('tercera', 'Tercera'),
        ('especial', 'Edición especial'),
        ('revisada', 'Edición revisada'),
    ]

    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)    
    editorial = models.CharField(max_length=100)
    año = models.PositiveIntegerField()
    isbn = models.CharField(max_length=13, unique=True)
    ejemplares_disponibles = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    sinopsis = models.TextField(blank=True, null=True)
    num_paginas = models.PositiveIntegerField(blank=True, null=True)
    idioma = models.CharField(max_length=50, choices=IDIOMAS, blank=True, null=True)
    formato = models.CharField(max_length=100, choices=FORMATOS, blank=True, null=True)
    edicion = models.CharField(max_length=100, choices=EDICIONES, blank=True, null=True)
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)
    subcategoria = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} por {self.autor}"
    
    def get_subcategoria_choices(self):
        return self.SUBCATEGORIAS.get(self.categoria.lower(), [])
    
    def get_subcategoria_display(self):
        subcats = dict(self.SUBCATEGORIAS.get(self.categoria, []))
        return subcats.get(self.subcategoria, "")


class Prestamo(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('devuelto', 'Devuelto'),
        ('en_retraso', 'En Retraso'),
    ]

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libros, on_delete=models.CASCADE)
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    fecha_devolucion_estimada = models.DateField()
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Prestamo de {self.libro.titulo} por {self.usuario.username}"
    
class FiltroLibrosForm(forms.Form):
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + Libros.CATEGORIAS,
        required=False,
    )
    titulo = forms.CharField(max_length=100, required=False)

class PrestamoForm(forms.ModelForm):
    libro = forms.ModelChoiceField(queryset=Libros.objects.none(), empty_label=None, label='Libro')

    class Meta:
        model = Prestamo
        fields = ['libro', 'fecha_devolucion_estimada']
