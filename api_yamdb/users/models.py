from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from api_yamdb.settings import MAX_LENGTH_FIELD_150

from .validators import validate_username_not_me


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
            validate_username_not_me,
            UnicodeUsernameValidator()
        ],
        max_length=MAX_LENGTH_FIELD_150,
        unique=True,
    )
    email = models.EmailField(
        'E-mail',
        unique=True,
    )
    role = models.CharField(
        'Роль',
        default=USER,
        choices=CHOICES_ROLE,
        max_length=MAX_LENGTH_FIELD_150,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator_role(self):
        return self.role == self.MODERATOR or self.is_superuser
