from django.contrib import admin
from .models import AdvisorMessage, AdvisorSession


class AdvisorMessageInline(admin.TabularInline):
    model = AdvisorMessage
    extra = 0
    readonly_fields = ('role', 'content', 'sources', 'created_at')


@admin.register(AdvisorSession)
class AdvisorSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    inlines = [AdvisorMessageInline]
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(AdvisorMessage)
class AdvisorMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'created_at')
    list_filter = ('role',)
    readonly_fields = ('session', 'role', 'content', 'sources', 'created_at')
