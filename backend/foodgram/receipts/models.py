from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """ Модель тега. """

    name = models.CharField(
        'Название тега',
        unique=True,
        max_length=200
    )
    color = models.CharField(
        'Цвет',
        unique=True,
        max_length=7
    )
    slug = models.SlugField(
        'Slug',
        unique=True,
        max_length=200
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    text = models.TextField(
        'Описание рецепта',
        null=True
    )

    title = models.CharField(
        max_length=255,
        verbose_name='Название рецепта'
    )

    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        default=None,
        null=True,
        blank=True
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        related_name='ingredient'
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэг',
        related_name='tag'
    )

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        'Время пубикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    """ Модель связи ингредиента и рецепта. """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
    )

    class Meta:
        ordering = ('recipe',)

    def __str__(self):
        return self.recipe


class RecipeTag(models.Model):
    """ Модель связи тега и рецепта. """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        ordering = ('tag',)

    def __str__(self):
        return self.tag


class Favorite(models.Model):
    """ Модель избранного. """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites',
    )

    class Meta:
        ordering = ('recipe',)

    def __str__(self):
        return self.recipe


class ShoppingCart(models.Model):
    """ Модель корзины. """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart',
    )

    class Meta:
        ordering = ('recipe',)

    def __str__(self):
        return self.recipe
