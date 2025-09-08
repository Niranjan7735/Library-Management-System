from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book
from django import forms

class BookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure availability_status is checked by default for new books
        if not self.instance.pk:
            self.fields['availability_status'].initial = True

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'quantity', 'description', 'published_date', 'availability_status']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter book title', 'class': 'form-control'}),
            'author': forms.TextInput(attrs={'placeholder': 'Enter author name', 'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'placeholder': 'Enter ISBN number', 'class': 'form-control'}),
            'category': forms.TextInput(attrs={'placeholder': 'Enter book category', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter book description', 'class': 'form-control', 'rows': 3}),
            'availability_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

@login_required
def book_list(request):
    """Display list of all books with search and filter options"""
    books = Book.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Filter by availability
    availability_filter = request.GET.get('availability', '')
    if availability_filter == 'available':
        books = books.filter(availability_status=True)
    elif availability_filter == 'unavailable':
        books = books.filter(availability_status=False)
    
    # Calculate available books count
    available_count = books.filter(availability_status=True).count()
    
    context = {
        'books': books,
        'available_count': available_count,
        'search_query': search_query,
        'availability_filter': availability_filter,
        'is_staff': request.user.is_staff,
    }
    return render(request, 'books/books_list.html', context)

@login_required
def book_detail(request, book_id):
    """Display detailed information about a specific book"""
    book = get_object_or_404(Book, id=book_id)
    context = {
        'book': book,
        'is_staff': request.user.is_staff,
        'user': request.user,
        'base_template': 'admin_base.html' if request.user.is_staff else 'base.html',
    }
    return render(request, 'books/book_detail.html', context)

@login_required
def add_book(request):
    """View to add a new book."""
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users to home
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
            return redirect('book_list')
    else:
        form = BookForm()
    
    return render(request, 'books/add_book.html', {'form': form, 'is_staff': request.user.is_staff})

@login_required
def delete_book(request, book_id):
    """View to delete a book."""
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users to home
    
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, f"Book '{book.title}' deleted successfully!")
        return redirect('book_list')
    
    # If not POST, show confirmation page
    return render(request, 'books/delete_book.html', {'book': book, 'is_staff': request.user.is_staff})

@login_required
def edit_book(request, book_id):
    """View to edit an existing book."""
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users to home
    
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"Book '{book.title}' updated successfully!")
            return redirect('book_detail', book_id=book.id)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'books/edit_book.html', {'form': form, 'book': book, 'is_staff': request.user.is_staff})
