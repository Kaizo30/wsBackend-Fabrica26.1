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

    try:
        # usa o parâmetro "imdb_id" como ID da TMDb por compatibilidade com a rota atual
        tmdb_id = imdb_id

        # ---------------------------
        # 1) detalhes principais do filme
        # ---------------------------
        detalhes_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        detalhes_params = {
            "api_key": TMDB_API_KEY,
            "language": "pt-BR",
        }

        detalhes_response = requests.get(detalhes_url, params=detalhes_params, timeout=10)
        detalhes_response.raise_for_status()
        dados = detalhes_response.json()

        # se vier erro da API
        if dados.get("success") is False:
            erro = "filme não encontrado."
        else:
            # ---------------------------
            # 2) créditos (diretor + elenco)
            # ---------------------------
            credits_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
            credits_params = {
                "api_key": TMDB_API_KEY,
                "language": "pt-BR",
            }

            credits_response = requests.get(credits_url, params=credits_params, timeout=10)
            credits_response.raise_for_status()
            credits_data = credits_response.json()

            # diretor
            diretor = "Não informado"
            crew = credits_data.get("crew", [])
            for pessoa in crew:
                if pessoa.get("job") == "Director":
                    diretor = pessoa.get("name", "Não informado")
                    break

            # atores principais (top 5)
            elenco = credits_data.get("cast", [])
            atores = ", ".join([ator.get("name", "") for ator in elenco[:5] if ator.get("name")]) or "Não informado"

            # ---------------------------
            # 3) vídeos (trailer real)
            # ---------------------------
            videos_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
            videos_params = {
                "api_key": TMDB_API_KEY,
                "language": "pt-BR",
            }

            videos_response = requests.get(videos_url, params=videos_params, timeout=10)
            videos_response.raise_for_status()
            videos_data = videos_response.json()

            videos = videos_data.get("results", [])

            # tenta trailer oficial do YouTube
            trailer_key = None

            # prioridade 1: trailer em pt-BR
            for video in videos:
                if (
                    video.get("site") == "YouTube"
                    and video.get("type") == "Trailer"
                    and video.get("official") is True
                ):
                    trailer_key = video.get("key")
                    break

            # prioridade 2: qualquer trailer no YouTube
            if not trailer_key:
                for video in videos:
                    if (
                        video.get("site") == "YouTube"
                        and video.get("type") == "Trailer"
                    ):
                        trailer_key = video.get("key")
                        break

            # fallback: busca no YouTube
            titulo_busca = dados.get("title", "")
            ano_busca = dados.get("release_date", "")[:4] if dados.get("release_date") else ""
            busca_trailer = f"{titulo_busca} {ano_busca} trailer"

            trailer_busca_url = f"https://www.youtube.com/results?search_query={quote_plus(busca_trailer)}"

            if trailer_key:
                trailer_url = f"https://www.youtube.com/embed/{trailer_key}"

            # ---------------------------
            # 4) montar objeto no formato q teu template já entende
            # ---------------------------
            poster_path = dados.get("poster_path")
            backdrop_path = dados.get("backdrop_path")

            poster_url = (
                f"https://image.tmdb.org/t/p/w500{poster_path}"
                if poster_path else
                "https://via.placeholder.com/300x450?text=Sem+Imagem"
            )

            backdrop_url = (
                f"https://image.tmdb.org/t/p/original{backdrop_path}"
                if backdrop_path else
                None
            )

            generos = ", ".join([g.get("name", "") for g in dados.get("genres", []) if g.get("name")]) or "Não informado"

            filme = {
                "Title": dados.get("title", "Sem título"),
                "Year": dados.get("release_date", "")[:4] if dados.get("release_date") else "N/A",
                "Released": dados.get("release_date", "Não informado"),
                "Genre": generos,
                "Runtime": f"{dados.get('runtime')} min" if dados.get("runtime") else "Não informado",
                "Plot": dados.get("overview", "Sinopse não disponível.") or "Sinopse não disponível.",
                "Poster": poster_url,
                "Backdrop": backdrop_url,
                "Director": diretor,
                "Actors": atores,
                "imdbRating": str(dados.get("vote_average", "N/A")),
                "VoteCount": dados.get("vote_count", 0),
            }

    except requests.RequestException:
        erro = "erro ao conectar com a tmdb."

    return render(request, "cinevault/api/detalhes_filme.html", {
        "filme": filme,
        "erro": erro,
        "trailer_url": trailer_url,
        "trailer_busca_url": trailer_busca_url,
    })