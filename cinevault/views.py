import os
import requests
from dotenv import load_dotenv
from django.shortcuts import render, get_object_or_404, redirect
from .models import Categoria, Filme
from .forms import CategoriaForm, FilmeForm

load_dotenv()


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
# API EXTERNA - OMDb (BUSCA MÚLTIPLA)
# -------------------

def buscar_filme_api(request):
    resultados = []
    erro = None

    titulo = request.GET.get('titulo')

    if titulo:
        api_key = os.getenv("OMDB_API_KEY")

        if not api_key:
            erro = "chave da API não encontrada no arquivo .env"
        else:
            url = f"http://www.omdbapi.com/?s={titulo}&apikey={api_key}"

            try:
                resposta = requests.get(url)
                dados = resposta.json()

                if dados.get("Response") == "True":
                    resultados = dados.get("Search", [])
                else:
                    erro = dados.get("Error", "nenhum filme encontrado.")

            except Exception as e:
                erro = f"erro ao conectar com a api: {str(e)}"

    contexto = {
        'resultados': resultados,
        'erro': erro,
    }

    return render(request, 'cinevault/api/buscar_filme.html', contexto)


# -------------------
# DETALHES DO FILME PELA API
# -------------------

def detalhes_filme_api(request, imdb_id):
    filme = None
    erro = None

    api_key = os.getenv("OMDB_API_KEY")

    if not api_key:
        erro = "chave da API não encontrada no arquivo .env"
    else:
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}&plot=full"

        try:
            resposta = requests.get(url)
            dados = resposta.json()

            if dados.get("Response") == "True":
                filme = dados
            else:
                erro = dados.get("Error", "filme não encontrado.")

        except Exception as e:
            erro = f"erro ao conectar com a api: {str(e)}"

    contexto = {
        'filme': filme,
        'erro': erro,
    }

    return render(request, 'cinevault/api/detalhes_filme.html', contexto)