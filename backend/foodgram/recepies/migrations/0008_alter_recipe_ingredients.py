# Generated by Django 4.2 on 2023-05-24 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0007_alter_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recepies.RecipeIngredient', to='recepies.ingredient', verbose_name='Ингридиенты'),
        ),
    ]