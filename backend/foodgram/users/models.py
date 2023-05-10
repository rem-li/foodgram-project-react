from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser):
    StatusUser = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )
    password = models.CharField(
        # max_length=settings.LEN_PASSWORD, 
        max_length=100, 
        blank=True, null=True)
    username = models.CharField(
        # max_length=settings.LEN_USER_FIELDS, 
        max_length=100,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
        validators=[validate_username]
    )
    email = models.EmailField(
        # max_length=settings.LEN_EMAIL, 
        max_length=100,
        verbose_name='email',
        unique=True
    )
    first_name = models.CharField(
        # max_length=settings.LEN_USER_FIELDS, 
        max_length=100,
        verbose_name='имя',
        blank=True
    )
    last_name = models.CharField(
        # max_length=settings.LEN_USER_FIELDS, 
        max_length=100,
        verbose_name='фамилия',
        blank=True
    )
    bio = models.TextField(
        verbose_name='биография',
        blank=True
    )
    role = models.CharField(
        'Статус пользователя',
        default=USER,
        choices=StatusUser,
        max_length=max(len(role) for role, _ in StatusUser)
    )

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    # def __str__(self):
    #     return self.username[:settings.LEN_TEXT]

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'
