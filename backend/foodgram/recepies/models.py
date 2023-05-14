from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название ингридиента'
        )
    units = models.CharField(
        max_length=10, default='', verbose_name='Единицы измерения'
        )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название тэга')
    hexcolor = models.CharField(max_length=7, default="#ffffff")
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Aвтор'
        )
    name = models.CharField(max_length=100, verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Изображение')
    text = models.TextField(verbose_name='Текст рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингридиенты'
        )
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
        )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления'
        )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        unique_together = ('recipe', 'ingredients')


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        unique_together = ('shopping_list', 'recipe', 'ingredient')
        verbose_name = 'Пункт списка покупок'
        verbose_name_plural = 'Пункты списков покупок'
