import re

from rest_framework.exceptions import ValidationError


def validate_username(value):
    if value in 'me':
        raise ValidationError(
            'Использовать имя me запрещено'
        )
    for i in value:
        if not re.search(r'^[\w.@+-]+$', i):
            raise ValidationError(
                f'Импользовать символ {i} в имени запрещено',
            )
