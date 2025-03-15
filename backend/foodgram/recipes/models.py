from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='HEX цвет',
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения',
    )

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
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
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
    short_id = models.CharField(max_length=10, unique=True,
                                blank=True, null=True)

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
    amount = models.IntegerField(
        verbose_name='Количество',
    )


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

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
