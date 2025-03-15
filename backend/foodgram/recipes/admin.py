from django.contrib import admin

from recipes.models import (Tag, Ingredient, Recipe,
                            RecipeIngredient, Favorite, ShoppingCart)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name',
                    'image', 'text', 'cooking_time',
                    'get_tags', 'get_ingredients', 'published_date')
    list_filter = ('name', 'author', 'tags', )
    search_fields = ('name', 'author', )

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = "Теги"

    def get_ingredients(self, obj):
        return ", ".join([ri.ingredient.name
                          for ri in obj.recipeingredient_set.all()])
    get_ingredients.short_description = "Ингредиенты"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', )
