from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'borrow_date', 'return_date', 'status', 'fine_amount')
    search_fields = ('book__title', 'member__name')
    list_filter = ('status', 'borrow_date')
