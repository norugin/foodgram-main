import shortuuid
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer

from recipes.models import Recipe, Tag, Ingredient
from api.serializers import (RecipeSerializer, TagSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             UserSerializer, SubscriptionSerializer,
                             UserAvatarSerializer, FavoriteSerializer,
                             ShoppingCartSerializer)
from api.utils import shopping_cart
from api.permissions import (IsOwnerOrAdminOrReadOnly,
                             IsCurrentUserOrAdminOrReadOnly)
from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import ApiPagination
from api.constants import SHORT_ID_LENGTH
from users.models import User


class BaseReadOnlyViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [AllowAny]


class TagViewSet(BaseReadOnlyViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(BaseReadOnlyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ['^name']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    pagination_class = ApiPagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            if user.favorite_recipes.filter(recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        favorite_item = user.favorite_recipes.filter(recipe=recipe)
        if favorite_item.exists():
            favorite_item.delete()
            return Response('Рецепт успешно удалён из избранного.',
                            status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'Рецепт не существует в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            if user.shopping_cart.filter(recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        shopping_cart_item = user.shopping_cart.filter(recipe=recipe)
        if shopping_cart_item.exists():
            shopping_cart_item.delete()
            return Response('Рецепт успешно удалён из списка покупок.',
                            status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'Рецепт не существует в списке покупок'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.shopping_cart.exists():
            return shopping_cart(self, request, user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)

        if not recipe.short_id:
            recipe.short_id = shortuuid.uuid()[:SHORT_ID_LENGTH]
            recipe.save(update_fields=['short_id'])

        short_link = f'{settings.SITE_URL}/s/{recipe.short_id}'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnly, )
    pagination_class = ApiPagination
    serializer_class = UserSerializer

    @action(methods=['get'], permission_classes=[IsAuthenticated],
            detail=False)
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            if user.follower.filter(author=author).exists():
                return Response({'errors': 'Вы уже подписаны'
                                           ' на этого пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = SubscriptionSerializer(
                data=request.data,
                context={'request': request, 'author': author}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, subscriber=user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        subscription = user.follower.filter(author=author)
        if subscription.exists():
            subscription.delete()
            return Response({'message': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'Подписка не существует'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], permission_classes=[IsAuthenticated],
            detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response('Пароль успешно изменен',
                        status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], permission_classes=[IsAuthenticated],
            detail=False)
    def subscriptions(self, request):
        subscriptions = self.request.user.follower.all()
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(pages, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['put', 'delete'], permission_classes=[IsAuthenticated],
            detail=False, url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if 'avatar' not in request.data:
            return Response({'avatar': 'Это обязательное поле'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UserAvatarSerializer(user, data=request.data,
                                          partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
