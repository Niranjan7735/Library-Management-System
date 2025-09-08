from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from books.models import Book
from members.models import Member
from transactions.models import Transaction


def contact(request):
    """Contact Us page view"""
    return render(request, 'contact.html')


def about(request):
    """About Us page view"""
    return render(request, 'about.html')


@login_required(login_url='/login/')
def home(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    latest_books = Book.objects.all().order_by('-created_at')[:5]
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    active_transactions = Transaction.objects.filter(status='borrowed').count()

    context = {
        'latest_books': latest_books,
        'total_books': total_books,
        'total_members': total_members,
        'active_transactions': active_transactions,
    }
    return render(request, 'home.html', context)


@login_required(login_url='/login/')
def admin_dashboard(request):
    print(f"User accessing admin dashboard: {request.user.username}, Authenticated: {request.user.is_authenticated}, Staff: {request.user.is_staff}")
    """Admin dashboard view with statistics and management options"""
    if not request.user.is_staff:
        # Redirect non-admin users to home
        return redirect('home')

    total_books = Book.objects.count()
    total_members = Member.objects.count()
    borrowed_books = Transaction.objects.filter(status='borrowed').count()
    overdue_books = Transaction.objects.filter(status='overdue').count()

    context = {
        'is_staff': request.user.is_staff,
        'total_books': total_books,
        'total_members': total_members,
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books,
    }
    return render(request, 'admin_dashboard.html', context)

def custom_login(request):
    if request.user.is_authenticated:
        # Redirect authenticated users away from login page
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                try:
                    member = Member.objects.get(user=user)
                    if member.password == password:
                        return redirect('home')
                    else:
                        messages.error(request, "Invalid password for member account.")
                        return render(request, 'login.html')
                except Member.DoesNotExist:
                    return redirect('home')
        else:
            try:
                member = Member.objects.get(email=username)
            except Member.DoesNotExist:
                try:
                    member = Member.objects.get(username=username)
                except Member.DoesNotExist:
                    messages.error(request, "Invalid username or password.")
                    return render(request, 'login.html')
            
            if member.password == password:
                if not member.user:
                    user = User.objects.create_user(
                        username=member.username,
                        email=member.email,
                        password=password
                    )
                    member.user = user
                    member.save()
                else:
                    if not member.user.check_password(password):
                        member.user.set_password(password)
                        member.user.save()
                
                login(request, member.user)
                return redirect('home')
            else:
                messages.error(request, "Invalid password for member account.")
                return render(request, 'login.html')
    
    return render(request, 'login.html')
