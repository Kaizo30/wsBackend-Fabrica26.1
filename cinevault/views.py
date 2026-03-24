import os
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv
from django.shortcuts import render, get_object_or_404, redirect
from .models import Categoria, Filme
from .forms import CategoriaForm, FilmeForm

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"


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
# FUNÇÕES AUXILIARES TMDb
# -------------------

def montar_url_imagem_tmdb(caminho_imagem):
    if caminho_imagem:
        return f"{TMDB_IMAGE_BASE_URL}{caminho_imagem}"
    return None


def montar_url_backdrop_tmdb(caminho_backdrop):
    if caminho_backdrop:
        return f"{TMDB_BACKDROP_BASE_URL}{caminho_backdrop}"
    return None


def buscar_filmes_tmdb(titulo):
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY não configurada no .env")

    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": titulo,
        "language": "pt-BR",
        "include_adult": False,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    dados = response.json()

    resultados = []

    for filme in dados.get("results", []):
        resultados.append({
            "Title": filme.get("title"),
            "Year": (filme.get("release_date") or "")[:4] if filme.get("release_date") else "N/A",
            "Type": "movie",
            "Poster": montar_url_imagem_tmdb(filme.get("poster_path")) or "N/A",
            "imdbID": str(filme.get("id")),  # mantemos o nome imdbID para não quebrar template/rota
        })

    return resultados


def obter_trailer_tmdb(videos):
    resultados = videos.get("results", []) if videos else []

    # prioridade 1: trailer oficial no youtube
    for video in resultados:
        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
        ):
            key = video.get("key")
            if key:
                return {
                    "watch_url": f"https://www.youtube.com/watch?v={key}",
                    "embed_url": f"https://www.youtube.com/embed/{key}",
                }

    # prioridade 2: qualquer trailer no youtube
    for video in resultados:
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            key = video.get("key")
            if key:
                return {
                    "watch_url": f"https://www.youtube.com/watch?v={key}",
                    "embed_url": f"https://www.youtube.com/embed/{key}",
                }

    # prioridade 3: teaser no youtube
    for video in resultados:
        if video.get("site") == "YouTube" and video.get("type") == "Teaser":
            key = video.get("key")
            if key:
                return {
                    "watch_url": f"https://www.youtube.com/watch?v={key}",
                    "embed_url": f"https://www.youtube.com/embed/{key}",
                }

    return None


def buscar_detalhes_tmdb(tmdb_id):
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY não configurada no .env")

    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR",
        "append_to_response": "videos",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    dados = response.json()

    trailer = obter_trailer_tmdb(dados.get("videos", {}))

    titulo = dados.get("title", "")
    ano = (dados.get("release_date") or "")[:4] if dados.get("release_date") else ""

    trailer_busca_url = f"https://www.youtube.com/results?search_query={quote_plus(f'{titulo} {ano} trailer oficial')}"

    generos = ", ".join([g.get("name", "") for g in dados.get("genres", []) if g.get("name")])

    diretores = []
    elenco = []

    # ainda não vamos usar credits aqui pra não complicar demais nessa etapa
    # isso pode entrar numa próxima melhoria

    filme_formatado = {
        "Title": dados.get("title", "Título não disponível"),
        "Year": ano or "N/A",
        "Released": dados.get("release_date", "N/A"),
        "Genre": generos or "N/A",
        "Runtime": f"{dados.get('runtime')} min" if dados.get("runtime") else "N/A",
        "Director": ", ".join(diretores) if diretores else "Não informado",
        "Actors": ", ".join(elenco) if elenco else "Não informado",
        "Plot": dados.get("overview") or "Sinopse não disponível em português.",
        "Language": dados.get("original_language", "N/A").upper(),
        "Poster": montar_url_imagem_tmdb(dados.get("poster_path")) or "N/A",
        "Backdrop": montar_url_backdrop_tmdb(dados.get("backdrop_path")),
        "imdbRating": dados.get("vote_average", "N/A"),
    }

    return filme_formatado, trailer, trailer_busca_url


# -------------------
# API EXTERNA - TMDb (MIGRAÇÃO SEGURA)
# -------------------

def buscar_filme_api(request):
    resultados = []
    erro = None
    titulo = request.GET.get("titulo", "").strip()

    if titulo:
        try:
            resultados = buscar_filmes_tmdb(titulo)

            if not resultados:
                erro = "Nenhum filme encontrado."
        except ValueError as e:
            erro = str(e)
        except requests.RequestException:
            erro = "Erro ao conectar com a TMDb."

    return render(request, "cinevault/api/buscar_filme.html", {
        "resultados": resultados,
        "erro": erro,
    })


def detalhes_filme_api(request, imdb_id):
    filme = None
    erro = None
    trailer_url = None
    trailer_busca_url = None
    trailer_embed_url = None

    try:
        filme, trailer, trailer_busca_url = buscar_detalhes_tmdb(imdb_id)

        if trailer:
            trailer_url = trailer.get("watch_url")
            trailer_embed_url = trailer.get("embed_url")
    except ValueError as e:
        erro = str(e)
    except requests.RequestException:
        erro = "Erro ao conectar com a TMDb."

    return render(request, "cinevault/api/detalhes_filme.html", {
        "filme": filme,
        "erro": erro,
        "trailer_url": trailer_url,
        "trailer_embed_url": trailer_embed_url,
        "trailer_busca_url": trailer_busca_url,
    })