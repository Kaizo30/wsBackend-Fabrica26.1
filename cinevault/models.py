from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class Filme(models.Model):
    titulo = models.CharField(max_length=200)
    diretor = models.CharField(max_length=100)
    ano = models.PositiveIntegerField()
    descricao = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='filmes')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo