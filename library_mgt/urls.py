"""library_mgt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home, admin_dashboard, custom_login, contact, about

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('books/', include('books.urls')),
    path('members/', include('members.urls')),
    path('transactions/', include('transactions.urls')),
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', lambda request: redirect('home'), name='root_redirect'),  
]
