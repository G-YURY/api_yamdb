from django.core.exceptions import ValidationError


def validate_username_not_me(value):
    if 'me' in value:
        raise ValidationError(
            ('Имя пользователя не может быть `me`.'),
            params={'value': value},
        )
