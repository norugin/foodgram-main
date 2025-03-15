from datetime import date

from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import RecipeIngredient


def shopping_cart(self, request, author):
    shopping_cart_instance = author.shopping_cart.first()
    sum_ingredients_in_recipes = RecipeIngredient.objects.filter(
        recipe__shopping_cart=shopping_cart_instance
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)
    ).order_by('amounts')

    today = date.today().strftime("%d-%m-%Y")
    shopping_list = f'Список покупок на: {today}\n\n'
    for ingredient in sum_ingredients_in_recipes:
        shopping_list += (
            f'{ingredient["ingredient__name"]} - '
            f'{ingredient["amounts"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
    filename = 'shopping_list.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
