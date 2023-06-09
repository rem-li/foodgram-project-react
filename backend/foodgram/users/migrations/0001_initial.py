# Generated by Django 4.2 on 2023-05-14 13:27

import django.contrib.auth.models
from django.conf import settings
from django.db import migrations, models

import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recepies', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('password', models.CharField(blank=True, max_length=128, null=True)),
                ('username', models.CharField(error_messages={'unique': 'Пользователь с таким именем уже существует.'}, help_text='Обязательное поле. Максимальная длина 150 символов. Только буквы, цифры и символы @/./+/-/_ .', max_length=150, unique=True, validators=[users.validators.validate_username])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='имя')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='фамилия')),
                ('bio', models.TextField(blank=True, verbose_name='биография')),
                ('role', models.CharField(choices=[('admin', 'Администратор'), ('moderator', 'Модератор'), ('user', 'Пользователь')], default='user', max_length=20, verbose_name='Статус пользователя')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('favorite_recipes', models.ManyToManyField(blank=True, related_name='favorited_by', to='recepies.recipe')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('subscriptions', models.ManyToManyField(related_name='subscribers', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
