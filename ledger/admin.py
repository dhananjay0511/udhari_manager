from django.contrib import admin
from .models import Person, Transaction


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "phone", "opening_balance", "created_at")
    list_filter = ("user",)
    search_fields = ("name", "phone")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("person", "user", "type", "amount", "date", "due_date")
    list_filter = ("type", "user")
    search_fields = ("person__name", "description")
    date_hierarchy = "date"
