from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from books.models import Book
from members.models import Member
from .models import Transaction


@login_required
def borrow_book(request, book_id):
    """Borrow a single book directly from its detail page"""
    if request.method == 'POST':
        try:
            book = Book.objects.get(id=book_id)

            # Get or create member for the current user
            try:
                member = request.user.member
            except (AttributeError, Member.DoesNotExist):
                # Try to find an existing member with the user's email
                user_email = request.user.email or f"{request.user.username}@example.com"

                # Check if a member with this email already exists
                try:
                    member = Member.objects.get(email=user_email)
                    # Link the member to the current user
                    member.user = request.user
                    member.save()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        pass  # Don't show info message for AJAX
                    else:
                        messages.info(request, 'Linked your account to existing member profile.')
                except Member.DoesNotExist:
                    # Create a temporary member profile for the user
                    # Generate a unique email if needed
                    base_email = user_email
                    counter = 1
                    while Member.objects.filter(email=user_email).exists():
                        user_email = f"{request.user.username}{counter}@example.com"
                        counter += 1

                    member = Member.objects.create(
                        user=request.user,
                        name=request.user.username,
                        email=user_email,
                        phone="",
                        address="",
                        membership_date=timezone.now().date(),
                        status='active'
                    )
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        pass  # Don't show info message for AJAX
                    else:
                        messages.info(request, 'Temporary member profile created for borrowing.')

            # Check if member is active
            if member.status != 'active':
                error_message = 'Your account is not active and cannot borrow books.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    })
                messages.error(request, error_message)
                return redirect('book_detail', book_id=book_id)

            # Check if member already borrowed this book and not returned yet
            existing_borrow = Transaction.objects.filter(book=book, member=member, status='borrowed').exists()
            if existing_borrow:
                error_message = 'You have already borrowed this book and not returned it yet.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    })
                messages.error(request, error_message)
                return redirect('book_detail', book_id=book_id)

            # Check available copies
            borrowed_count = Transaction.objects.filter(book=book, status='borrowed').count()
            if borrowed_count >= book.quantity:
                error_message = 'All copies of this book are currently borrowed.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    })
                messages.error(request, error_message)
                return redirect('book_detail', book_id=book_id)

            # Create transaction
            Transaction.objects.create(
                book=book,
                member=member,
                borrow_date=timezone.now().date(),
                status='borrowed'
            )

            # Update book availability status
            book.update_availability_status()

            success_message = f'Book "{book.title}" borrowed successfully!'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'available_quantity': book.available_quantity,
                    'availability_status': book.availability_status
                })
            else:
                messages.success(request, success_message)
                return redirect('transaction_history')

        except Book.DoesNotExist:
            error_message = 'Book not found.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            messages.error(request, error_message)
            return redirect('book_list')
    else:
        # If accessed via GET, redirect to book detail
        return redirect('book_detail', book_id=book_id)


@login_required
def return_book(request):
    """Return a borrowed book"""
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction')

        try:
            transaction = Transaction.objects.get(id=transaction_id, status='borrowed')

            # Check if user has permission to return this book
            if not request.user.is_staff:
                try:
                    user_member = request.user.member
                    if user_member.id != transaction.member.id:
                        error_message = "You can only return your own borrowed books."
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'message': error_message
                            })
                        messages.error(request, error_message)
                        return redirect('return_book')
                except (AttributeError, Member.DoesNotExist):
                    error_message = "Member profile not found."
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': error_message
                        })
                    messages.error(request, error_message)
                    return redirect('return_book')

            # Update transaction
            transaction.return_date = timezone.now().date()
            transaction.status = 'returned'
            transaction.save()

            # Update book availability status
            book = Book.objects.get(id=transaction.book.id)
            book.update_availability_status()

            success_message = f'Book "{transaction.book.title}" returned successfully.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'book_title': transaction.book.title,
                    'return_date': transaction.return_date.strftime('%B %d, %Y')
                })
            else:
                messages.success(request, success_message)
                return redirect('transaction_history')

        except Transaction.DoesNotExist:
            error_message = 'Invalid transaction selected.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            messages.error(request, error_message)
            return redirect('return_book')

    # GET request - show form
    if request.user.is_staff:
        # Staff can see all borrowed books
        borrowed_books = Transaction.objects.filter(status='borrowed')
    else:
        # Regular users can only see their own borrowed books
        try:
            user_member = request.user.member
            borrowed_books = Transaction.objects.filter(status='borrowed', member=user_member)
        except (AttributeError, Member.DoesNotExist):
            borrowed_books = Transaction.objects.none()
            messages.info(request, "No member profile found. You haven't borrowed any books.")

    context = {
        'borrowed_books': borrowed_books,
        'is_staff': request.user.is_staff,
        'base_template': 'admin_base.html' if request.user.is_staff else 'base.html',
    }
    return render(request, 'transactions/return_form.html', context)


@login_required
def transaction_history(request):
    """Display transaction history"""
    if request.user.is_staff:
        # Staff/admin can see all transactions
        transactions = Transaction.objects.all().order_by('-borrow_date')
    else:
        # Regular users see only their own transactions
        try:
            member = request.user.member
            transactions = Transaction.objects.filter(member=member).order_by('-borrow_date')
        except (AttributeError, Member.DoesNotExist):
            transactions = Transaction.objects.none()

    # Check if the user is staff/admin
    is_staff = request.user.is_staff
    context = {
        'transactions': transactions,
        'is_staff': is_staff,
    }
    # Render the appropriate template based on user role
    if is_staff:
        return render(request, 'transactions/admin_transaction_history.html', context)
    else:
        return render(request, 'transactions/transaction_history.html', context)


@login_required
def borrow_book_form(request):
    """Form where admin/staff can select member + book to borrow"""
    if request.method == 'POST':
        member_id = request.POST.get('member')
        book_id = request.POST.get('book')

        try:
            book = Book.objects.get(id=book_id)
            member = Member.objects.get(id=member_id)

            # Check if member already borrowed this book and not returned yet
            existing_borrow = Transaction.objects.filter(book=book, member=member, status='borrowed').exists()
            if existing_borrow:
                messages.error(request, f'{member.name} has already borrowed this book and not returned it yet.')
                return redirect('home')

            # Check available copies
            borrowed_count = Transaction.objects.filter(book=book, status='borrowed').count()
            if borrowed_count >= book.quantity:
                messages.error(request, 'All copies of this book are currently borrowed.')
                return redirect('home')

            # Check if member is active
            if member.status != 'active':
                messages.error(request, 'This member account is not active and cannot borrow books.')
                return redirect('home')

            # Create transaction
            Transaction.objects.create(
                book=book,
                member=member,
                borrow_date=timezone.now().date(),
                status='borrowed'
            )

            # Update book availability status
            book.update_availability_status()

            messages.success(request, f'Book "{book.title}" borrowed successfully by {member.name}!')
            return redirect('home')

        except (Book.DoesNotExist, Member.DoesNotExist):
            messages.error(request, 'Invalid book or member selected.')
            return redirect('home')

    # GET request - show form
    members = Member.objects.filter(status='active').order_by('name')
    available_books = Book.objects.filter(availability_status=True).order_by('title')

    context = {
        'members': members,
        'available_books': available_books,
    }
    return render(request, 'transactions/borrow_book.html', context)
