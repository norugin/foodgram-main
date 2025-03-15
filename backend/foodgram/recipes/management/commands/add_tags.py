from django.core.management.base import BaseCommand
from recipes.models import Tag, Ingredient


class Command(BaseCommand):
    help = 'Добавить начальные теги'

    def handle(self, *args, **kwargs):
        Tag.objects.get_or_create(name="Завтрак",
                                  color="#FFA500", slug="breakfast")
        Tag.objects.get_or_create(name="Обед", color="#FF4500", slug="lunch")
        Tag.objects.get_or_create(name="Ужин", color="#8B0000", slug="dinner")
        Ingredient.objects.create(name="Tomato", measurement_unit="kg")
        Ingredient.objects.create(name="Cucumber", measurement_unit="kg")

        self.stdout.write(self.style.SUCCESS('Теги успешно добавлены'))
