from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    STATUS_CHOICES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )
    password = models.CharField(max_length=128, blank=True, null=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=(
            'Обязательное поле. Максимальная длина 150 символов. '
            'Только буквы, цифры и символы @/./+/-/_ .'
        ),
        validators=[validate_username],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=30, blank=True, verbose_name='имя'
        )
    last_name = models.CharField(
        max_length=30, blank=True, verbose_name='фамилия'
        )
    bio = models.TextField(blank=True, verbose_name='биография')
    role = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=USER,
        verbose_name='Статус пользователя'
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    favorite_recipes = models.ManyToManyField(
        'recepies.Recipe', blank=True, related_name='favorited_by'
        )
    subscriptions = models.ManyToManyField(
        'self', related_name='subscribers', symmetrical=False
        )

    def subscribe_to_user(self, target_user):
        self.subscriptions.add(target_user)

    def unsubscribe_from_user(self, target_user):
        self.subscriptions.remove(target_user)

    def is_subscribed_to(self, target_user):
        return self.subscriptions.filter(id=target_user.id).exists()

    @property
    def subscribed_users(self):
        return [s for s in self.subscriptions.all()]

    @property
    def target_users(self):
        return [s for s in self.subscribers.all()]
