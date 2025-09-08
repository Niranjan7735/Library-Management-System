from django.urls import path
from .views import member_list, member_detail, register, delete_member, add_member, edit_member

urlpatterns = [
    path('', member_list, name='member_list'),
    path('<int:member_id>/', member_detail, name='member_detail'),
    path('register/', register, name='register'),  # Fixed registration URL
    path('add/', add_member, name='add_member'),
    path('<int:member_id>/delete/', delete_member, name='delete_member'),
    path('<int:member_id>/edit/', edit_member, name='edit_member'),
]
