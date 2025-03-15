import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from users.models import User, Subscription
from recipes.models import (Recipe, Tag, Ingredient,
                            Favorite, ShoppingCart, RecipeIngredient)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name',
                  'password', 'id', 'avatar', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True},
                        'is_subscribed': {'read_only': True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'POST':
            if request.path.startswith('/api/users/'):
                data.pop('avatar', None)
                data.pop('is_subscribed', None)
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscription.objects.filter(subscriber=user,
                                               author=obj).exists()
        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source='author.id')
    avatar = serializers.ImageField(source='author.avatar', read_only=True)

    class Meta:
        model = Subscription
        fields = ('email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count', 'id', 'avatar')

    def get_is_subscribed(self, obj):
        print(obj)
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscription.objects.filter(subscriber=user,
                                               author=obj.author).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        if limit:
            limit = int(limit)
        recipes = Recipe.objects.filter(author=obj.author)
        if limit:
            recipes = recipes[:limit]
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.all().count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, subscriber=user):
            raise ValidationError(detail='Вы уже подписаны'
                                         ' на этого пользователя',
                                  code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(detail='Невозможно подписаться'
                                         ' на самого себя',
                                  code=status.HTTP_400_BAD_REQUEST)
        return data


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'image', 'id')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'slug', 'id')
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'id')
        read_only_fields = '__all__',


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.'
                                                        'measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('name', 'measurement_unit', 'amount', 'id')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("Изображение"
                                              " не может быть пустым!")
        try:
            format, imgstr = data.split(';base64,')
        except ValueError:
            raise serializers.ValidationError('Некорректный'
                                              ' формат изображения!')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time', 'id')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True,
                                          write_only=True,
                                          required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=obj).exists()
        return False

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {'ingredients': 'Нужно выбрать ингредиент!'}
            )
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredient, name=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients', 'Ингридиенты повторяются!'}
                )
            if int(item['amount']) <= 0:
                raise ValidationError(
                    {'amount': 'Количество должно быть больше 0!'}
                )
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError(
                {'tags': 'Необходимо выбрать тег!'}
            )
        tag_list = []
        for tag in tags:
            if tag in tag_list:
                raise ValidationError(
                    {'tags': 'Теги повторяются!'}
                )
            tag_list.append(tag)
        return value

    def add_tags(self, ingredients, tags, model):
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
        model.tags.set(tags)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags.all(),
                                               many=True).data
        representation['ingredients'] = (
            IngredientRecipeSerializer(instance.recipe_ingredient.all(),
                                       many=True).data)
        return representation

    def check_empty(self, ingredients, tags):
        if ingredients is None or len(ingredients) == 0:
            raise ValidationError({'ingredients': 'Нужно выбрать'
                                                  ' хотя бы один ингредиент!'})
        if tags is None or len(tags) == 0:
            raise ValidationError({'ingredients': 'Нужно выбрать'
                                                  ' хотя бы один тег!'})

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        self.check_empty(ingredients, tags)
        user = self.context.get('request').user
        if user.is_authenticated:
            validated_data['author'] = user
        recipe = super().create(validated_data)
        self.add_tags(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        self.check_empty(ingredients, tags)
        user = self.context.get('request').user
        if user.is_authenticated:
            validated_data['author'] = user
        instance.ingredients.clear()
        self.add_tags(ingredients, tags, instance)
        return super().update(instance, validated_data)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author', 'id',
                  'is_favorited', 'is_in_shopping_cart')


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            read_only=True)

    class Meta:
        model = Favorite
        fields = ('name', 'image', 'cooking_time', 'id')


class ShoppingCartSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('name', 'image', 'cooking_time', 'id')


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']
