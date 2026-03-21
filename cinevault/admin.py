from django.contrib import admin
from .models import Categoria, Filme


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')


@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'diretor', 'ano', 'categoria')
    list_filter = ('categoria', 'ano')
    search_fields = ('titulo', 'diretor')