from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipes, ShopCart,
                     Tags)


@admin.register(Tags)
class AdminTag(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


@admin.register(Ingredient)
class AdminIngredient(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeIngredientsInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Recipes)
class AdminRecipe(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'in_favorite')
    list_filter = ('name', 'author', 'tags', )
    inlines = (RecipeIngredientsInline,)

    def in_favorite(self, obj):
        return obj.favorite.count()


@admin.register(Favorite)
class AdminFavorite(admin.ModelAdmin):
    list_display = ('pk', 'author', 'recipe')


@admin.register(ShopCart)
class AdminShoppingList(admin.ModelAdmin):
    list_display = ('pk', 'author', 'recipe')
