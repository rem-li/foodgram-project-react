import json

from django.core.management.base import BaseCommand
from recepies.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('/data/ingredients.json', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            Ingredient.objects.create(
                name=item['name'],
                units=item['measurement_unit']
            )
