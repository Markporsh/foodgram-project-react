from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import User
EMPTY_MSG = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username', 'role'
    )
    search_fields = ('email', 'username', 'role')
    list_filter = ('email', 'username')


@admin.register(Recipe)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_author', 'title', 'text',
        'cooking_time', 'get_tags', 'get_ingredients',
        'pub_date', 'get_favorite_count'
    )
    search_fields = (
        'name', 'cooking_time',
        'author__email', 'ingredients'
    )
    list_filter = ('author', 'title', 'tags')
    # inlines = (ReceiptIngredientAdmin, ReceiptTagAdmin)
    empty_value_display = EMPTY_MSG

    @admin.display(description='Электронная почта автора')
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        return [x for x in obj.tags.all()]

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return [x.name for x in obj.ingredients.all()]

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()





@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',
    )
    search_fields = ('name', 'slug',)
    empty_value_display = EMPTY_MSG


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = EMPTY_MSG


@admin.register(Favorite)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_recipe'
    )
    empty_value_display = EMPTY_MSG

    @admin.display(
        description='Рецепт')
    def get_recipe(self, obj):
        return obj.recipe


@admin.register(ShoppingCart)
class SoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_recipe'
    )
    empty_value_display = EMPTY_MSG

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return obj.recipe
