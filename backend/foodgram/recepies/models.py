from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Class for ingredients"""

    name = models.CharField(max_length=100, verbose_name='Название ингридиента')
    units = models.CharField(max_length=10, default='', verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Tag(models.Model):
    """Class for tags"""

    name = models.CharField(max_length=100, verbose_name='Название тэга')
    hexcolor = models.CharField(max_length=7, default="#ffffff")
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Recipe(models.Model):
    """Class for recepies"""

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Aвтор')
    name = models.CharField(max_length=100, verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Изображение')
    text = models.TextField(verbose_name='Текст рецепта')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient', verbose_name='Ингридиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    time = models.PositiveIntegerField(verbose_name='Время приготовления')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        unique_together = ('recipe', 'ingredients')

