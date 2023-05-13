# Generated by Django 4.2 on 2023-05-13 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0001_initial'),
        ('users', '0003_alter_user_options_user_subscriptions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favorite_recipes',
            field=models.ManyToManyField(blank=True, related_name='favorited_by', to='recepies.recipe'),
        ),
    ]
