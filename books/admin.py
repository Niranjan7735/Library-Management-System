from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'availability_status', 'published_date')
    search_fields = ('title', 'author')
    list_filter = ('availability_status',)
