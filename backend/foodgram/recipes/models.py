from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from recipes.constants import (MAX_LENGTH_7, MAX_LENGTH_10,
                               MAX_LENGTH_50, MAX_LENGTH_200,
                               MIN_VALUE_VALIDATOR, MAX_VALUE_VALIDATOR)
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_200,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_50,
        unique=True,
        verbose_name='Слаг',
    )
    color = models.CharField(
        max_length=MAX_LENGTH_7,
        verbose_name='HEX цвет',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_50,
        verbose_name='Единицы измерения',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=MAX_LENGTH_200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_VALUE_VALIDATOR,
                                      'Минимальное время приготовления'),
                    MaxValueValidator(MAX_VALUE_VALIDATOR,
                                      'Максимальное время приготовления')],
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингриденты',
    )
    published_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    short_id = models.CharField(max_length=MAX_LENGTH_10, unique=True,
                                blank=True, null=True)

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Название рецепта',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Название ингридента',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_VALUE_VALIDATOR,
                              'Минимальное количество ингридиента'),
            MaxValueValidator(MAX_VALUE_VALIDATOR,
                              'Максимальное количество ингридиента'),
        ]
    )

    class Meta:
        ordering = ['recipe', 'ingredient']

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Рецепты',
    )

    class Meta:
        ordering = ['user', 'recipe']

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепты',
    )

    class Meta:
        ordering = ['user', 'recipe']

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
