from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipes,
                            ShopCart, Tags)
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    id = IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeReadSerializer(
        many=True, source='ingredient_list')
    author = CustomUserSerializer()
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = ('id', 'author', 'tags', 'image',
                  'ingredients', 'name', 'text',
                  'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(
                    author=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShopCart.objects.filter(
                    author=request.user, recipe=obj
                ).exists())


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeCreateSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'name', 'text',
                  'ingredients', 'image', 'cooking_time', 'id')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        ingredients_set = []
        if not ingredients:
            raise serializers.ValidationError(
                'Требуется выбрать хотя бы один ингредиент'
            )
        if not tags:
            raise serializers.ValidationError(
                'Требуется выбрать хотя бы один тег'
            )
        for ingredient in ingredients:
            amount = ingredient['amount']
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    'Этот ингредиент уже есть в рецепте'
                )
            elif int(amount) < 1:
                raise serializers.ValidationError(
                    'Неправильное количество ингредиентов'
                )
            else:
                ingredients_set.append(ingredient['id'])
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredienst = Ingredient.objects.get(id=ingredient['id'])
            IngredientRecipe.objects.bulk_create(
                [IngredientRecipe(
                    ingredient=ingredienst, recipe=recipe,
                    amount=ingredient['amount']
                )
                ]
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(ingredients=ingredients, recipe=instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = CustomUserSerializer.Meta.fields

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.recipe.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipe.count()
