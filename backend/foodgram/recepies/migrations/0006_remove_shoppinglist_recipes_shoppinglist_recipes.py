# Generated by Django 4.2 on 2023-05-24 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0005_remove_shoppinglist_recipes_shoppinglist_recipes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppinglist',
            name='recipes',
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='recipes',
            field=models.ManyToManyField(related_name='shopping_lists', to='recepies.recipe', verbose_name='Рецепты'),
        ),
    ]
