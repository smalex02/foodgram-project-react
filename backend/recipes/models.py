from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User

MAX_LENGTH_CHARFIELD = 256


class Ingredient(models.Model):
    """Ингредиент"""
    name = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения',
        help_text='Введите еденицу измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tags(models.Model):
    """Тег"""
    СOLOR_CHOICES = [
        ('#E26C2D', "Оранжевый"),
        ('#8fce00', "Салатовый"),
        ('#674ea7', "Пурпурный"),
        ('#2900FA', "Синий"),
        ('#FF0D05', "Красный"),
        ('#F7FF05', "Желтый"),
    ]
    name = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD,
        unique=True,
        verbose_name='Название тега',
        help_text='Введите название тега'
    )
    color = models.CharField(
        max_length=7,
        choices=СOLOR_CHOICES,
        unique=True,
        verbose_name='Цвет тега',
        help_text='Введите цвет'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug тега')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """"Рецепт"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD,
        verbose_name='Название рецепта'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1, 'Время приготовления должно быть больше одной минуты'
            ),
            MaxValueValidator(
                1440, 'Время приготовления должно быть не дольше суток'
            )
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты в блюде'
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Тег рецепта',
        related_name='recipe'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    """Модель связи рецепта и ингредиентов"""
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_list'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество в рецепте',
        validators=[MinValueValidator(1, 'Должен быть хотябы один ингредиент')]
    )

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'], name='recipe_ingredient_unique')
        ]


class BaseModel(models.Model):
    """Базовая модель"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'], name='unique_%(model_name)s')]


class ShopCart(BaseModel):
    """Список покупок"""

    class Meta:
        default_related_name = 'shop'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'


class Favorite(BaseModel):
    """Избранное"""

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
