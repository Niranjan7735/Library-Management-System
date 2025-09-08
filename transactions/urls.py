from django.urls import path
from .views import borrow_book, return_book, transaction_history, borrow_book_form

urlpatterns = [
path('borrow/<int:book_id>/', borrow_book, name='borrow_book'),
path('borrow-form/', borrow_book_form, name='borrow_book_form'),
path('return/', return_book, name='return_book'),
    path('history/', transaction_history, name='transaction_history'),
]
