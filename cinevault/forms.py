from django import forms
from .models import Categoria, Filme


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']


class FilmeForm(forms.ModelForm):
    class Meta:
        model = Filme
        fields = ['titulo', 'diretor', 'ano', 'descricao', 'categoria']