from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "is_default", "user")
    list_filter = ("category_type", "is_default")
    search_fields = ("name",)
