import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    now_year = dt.date.today().year
    if value > now_year:
        raise ValidationError('Проверьте год. Он больше текущего!')
    return value
