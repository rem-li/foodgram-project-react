# Generated by Django 4.2 on 2023-05-14 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='favorite_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество добавлений в избранное'),
        ),
    ]
