import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import validate_username
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    MODERATOR = 'moderator'
    USER = 'user'
    ADMIN = 'admin'

    CHOICES_ROLE = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )
    username = models.CharField(
        'Имя пользователя',
        validators=[
            validate_username,
            UnicodeUsernameValidator()
        ],
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        'E-mail',
        unique=True,
        blank=False,
        null=False)
    role = models.CharField(
        'Роль',
        default=USER,
        choices=CHOICES_ROLE,
        max_length=10,
        blank=True)
    bio = models.TextField(
        'Биография',
        blank=True)
    confirmation_code = models.UUIDField(
        'Код получения или обновления токена',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
