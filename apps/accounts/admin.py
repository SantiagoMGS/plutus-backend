from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "account_type", "currency", "balance", "user", "is_active")
    list_filter = ("account_type", "currency", "is_active")
    search_fields = ("name", "user__username")
