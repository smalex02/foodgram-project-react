from django.contrib import admin

from .models import User, Subscriber


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')


@admin.register(Subscriber)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
