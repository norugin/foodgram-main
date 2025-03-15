import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
import os


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.path.dirname(__file__), 'ingredients.csv')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден!'))
            return

        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(name=name,
                                                 measurement_unit=unit)

        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
