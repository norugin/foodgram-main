from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'password')
    list_filter = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author')
    list_filter = ('subscriber', 'author')
