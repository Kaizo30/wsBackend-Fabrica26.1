import requests
from decouple import config
from django.shortcuts import render, get_object_or_404, redirect
from .models import Categoria, Filme
from .forms import CategoriaForm, FilmeForm


def home(request):
    filmes = Filme.objects.all().order_by('-criado_em')
    return render(request, 'cinevault/home.html', {'filmes': filmes})


# -------------------
# CRUD CATEGORIA
# -------------------

def listar_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'cinevault/categoria_list.html', {'categorias': categorias})


def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'cinevault/categoria_form.html', {'form': form})


def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'cinevault/categoria_form.html', {'form': form})


def excluir_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return redirect('listar_categorias')
    return render(request, 'cinevault/categoria_confirm_delete.html', {'categoria': categoria})


# -------------------
# CRUD FILME
# -------------------

def listar_filmes(request):
    filmes = Filme.objects.select_related('categoria').all()
    return render(request, 'cinevault/filme_list.html', {'filmes': filmes})


def criar_filme(request):
    if request.method == 'POST':
        form = FilmeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_filmes')
    else:
        form = FilmeForm()
    return render(request, 'cinevault/filme_form.html', {'form': form})


def editar_filme(request, pk):
    filme = get_object_or_404(Filme, pk=pk)
    if request.method == 'POST':
        form = FilmeForm(request.POST, instance=filme)
        if form.is_valid():
            form.save()
            return redirect('listar_filmes')
    else:
        form = FilmeForm(instance=filme)
    return render(request, 'cinevault/filme_form.html', {'form': form})


def excluir_filme(request, pk):
    filme = get_object_or_404(Filme, pk=pk)
    if request.method == 'POST':
        filme.delete()
        return redirect('listar_filmes')
    return render(request, 'cinevault/filme_confirm_delete.html', {'filme': filme})


# -------------------
# API EXTERNA - OMDb
# -------------------

def buscar_filme_api(request):
    termo = request.GET.get('q')
    filmes_api = []
    erro = None

    if termo:
        api_key = config('OMDB_API_KEY')
        url = f"http://www.omdbapi.com/?apikey={api_key}&s={termo}"

        resposta = requests.get(url)

        if resposta.status_code == 200:
            dados = resposta.json()

            if dados.get("Response") == "True":
                filmes_api = dados.get("Search", [])
            else:
                erro = dados.get("Error", "Nenhum filme encontrado.")
        else:
            erro = "Erro ao consultar API externa."

    return render(request, 'cinevault/buscar_filme_api.html', {
        'filmes_api': filmes_api,
        'erro': erro
    })