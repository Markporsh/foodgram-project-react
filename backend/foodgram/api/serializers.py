from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from receipts.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, RecipeTag, ShoppingCart, Tag
)
from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]


class CustomUserSerializer(UserSerializer):
    """ Сериализатор модели пользователя. """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра модели Тег. """

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class ReceiptIngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор модели, связывающей ингредиенты и рецепт. """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class ReceiptTagSerializer(serializers.ModelSerializer):
    """ Сериализатор модели, связывающей ингредиенты и рецепт. """

    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = RecipeTag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра модели Ингредиенты. """

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class ReceiptSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра модели Рецепт. """

    tags = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    cooking_time = serializers.IntegerField(min_value=3, max_value=300)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]
        validators = []

    def get_tags(self, obj):
        tags = RecipeTag.objects.filter(recipe=obj)
        return ReceiptTagSerializer(tags, many=True).data

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ReceiptIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class AddIngredientReceiptSerializer(serializers.ModelSerializer):
    """ Сериализатор добавления ингредиента в рецепт. """

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1, max_value=100)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


# class AddTagReceiptSerializer(serializers.ModelSerializer):
#     """ Сериализатор добавления тега в рецепт. """
#
#     id = serializers.IntegerField()
#
#     class Meta:
#         model = RecipeIngredient
#         fields = ['id']


class CreateReceiptSerializer(serializers.ModelSerializer):
    """ Сериализатор создания/обновления рецепта. """

    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientReceiptSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = [
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_ids = set()
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_ids:
                raise serializers.ValidationError({
                   'ingredient': 'Ингредиенты должны быть уникальными!'
                })
            ingredients_ids.add(ingredient['id'])
        return data

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create_tags(self, tags, recipe):
        print(tags, '\ntag\n', recipe, 'recipe')
        RecipeTag.objects.bulk_create(
            [RecipeTag(
                recipe=recipe,
                tag=tag,
            ) for tag in tags]
        )
        print(Tag.objects.get(id=tags[0].id))

    def create(self, validated_data):
        """
        Создание рецепта.
        Доступно только авторизированному пользователю.
        """
        print(validated_data)

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Изменение рецепта.
        Доступно только автору.
        """
        print(validated_data, 'val')
        print(instance, 'instance')

        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.create_ingredients(ingredients, instance)
        self.create_tags(tags, instance)
        if validated_data.get('name'):
            instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image'):
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance

    def to_representation(self, instance):
        print(instance)
        return ReceiptSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения избранного. """

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ Сериализатор для списка покупок. """

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Избранное. """

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения подписок пользователя. """

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.favorites.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """ Сериализатор подписок. """

    class Meta:
        model = Subscription
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
            )
        ]

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(instance.author, context={
            'request': self.context.get('request')
        }).data

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError("Вы не можете подписаться на себя")
        return data


class UserListSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password',
        )
