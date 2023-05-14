from rest_framework.exceptions import ValidationError


def validate_username(value):
    if value in 'me':
        raise ValidationError(
            'Использовать имя me запрещено'
        )
