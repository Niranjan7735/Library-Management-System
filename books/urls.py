from django.urls import path
from .views import book_list, book_detail, add_book, delete_book, edit_book

urlpatterns = [
    path('', book_list, name='book_list'),
    path('<int:book_id>/', book_detail, name='book_detail'),
    path('add/', add_book, name='add_book'),
    path('<int:book_id>/edit/', edit_book, name='edit_book'),
    path('<int:book_id>/delete/', delete_book, name='delete_book'),
]
