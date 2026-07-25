from django.contrib import admin
from .models import Message, Favorite


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'listing', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('content',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'created_at')