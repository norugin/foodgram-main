from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Юзернэйм пользователя',
        validators=[validate_username, ],
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
    )
    avatar = models.ImageField(upload_to='users/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор",
    )

    def __str__(self):
        return f'{self.subscriber} подписан на: {self.author}'
