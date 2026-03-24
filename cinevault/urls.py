from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # categorias
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/excluir/<int:pk>/', views.excluir_categoria, name='excluir_categoria'),

    # filmes
    path('filmes/', views.listar_filmes, name='listar_filmes'),
    path('filmes/criar/', views.criar_filme, name='criar_filme'),
    path('filmes/editar/<int:pk>/', views.editar_filme, name='editar_filme'),
    path('filmes/excluir/<int:pk>/', views.excluir_filme, name='excluir_filme'),

    # api omdb
    path('buscar/', views.buscar_filme_api, name='buscar_filme_api'),
    path('buscar/<str:imdb_id>/', views.detalhes_filme_api, name='detalhes_filme_api'),
]