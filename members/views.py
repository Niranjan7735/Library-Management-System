from django.shortcuts import render, get_object_or_404, redirect
from .models import Member  # Assuming there's a Member model
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from .models import Member
from transactions.models import Transaction
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from .signals import create_member_profile

class RegistrationForm(forms.Form):
    is_staff = forms.BooleanField(required=False, initial=False, label="Grant admin privileges")
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

class MemberForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Member
        fields = ['name', 'email', 'phone', 'address', 'username', 'password']

@login_required
def member_list(request):
    """Display list of all library members"""
    # Only admin users can view members list
    if not request.user.is_staff:
        messages.error(request, "Only admin users can access member details.")
        return redirect('home')

    members = Member.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        members = members.filter(status=status_filter)

    # Calculate active members count
    active_count = members.filter(status='active').count()

    context = {
        'members': members,
        'active_count': active_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'is_staff': request.user.is_staff,
        'user': request.user,
    }
    return render(request, 'members/members_list.html', context)

@login_required
def member_detail(request, member_id):
    """Display detailed information about a specific member including borrowing history"""
    # Only admin users can view member details
    if not request.user.is_staff:
        messages.error(request, "Only admin users can access member details.")
        return redirect('home')

    member = get_object_or_404(Member, id=member_id)
    borrowing_history = Transaction.objects.filter(member=member).order_by('-borrow_date')

    context = {
        'member': member,
        'borrowing_history': borrowing_history,
        'is_staff': request.user.is_staff,
        'user': request.user,
    }
    return render(request, 'members/member_detail.html', context)

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            
            # Check if passwords match
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'register.html', {'form': form})
            
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return render(request, 'register.html', {'form': form})
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return render(request, 'register.html', {'form': form})
            
            # Create user and member with is_staff attribute
            try:
                # Disconnect signal to prevent automatic Member creation
                post_save.disconnect(create_member_profile, sender=User)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=form.cleaned_data['is_staff']
                )
                # Reconnect signal
                post_save.connect(create_member_profile, sender=User)

                member = Member.objects.create(
                    user=user,
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    membership_date=timezone.now().date(),
                    joined_date=timezone.now().date(),
                    username=username,
                    password=password
                )

                messages.success(request, "Registration successful! Please log in with your credentials.")
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f"An error occurred during registration: {str(e)}")
                return render(request, 'register.html', {'form': form})
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def add_member(request):
    """View to add a new member."""
    if not request.user.is_staff:
        messages.error(request, "Only admin users can add members.")
        return redirect('home')
    
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            from django.utils import timezone
            member.membership_date = timezone.now().date()
            member.joined_date = timezone.now().date()
            member.username = form.cleaned_data['username']

            # Check if the email already exists
            if Member.objects.filter(email=member.email).exists():
                messages.error(request, f"Email '{member.email}' already exists. Please choose a different email.")
                return render(request, 'members/add_member.html', {'form': form, 'is_staff': request.user.is_staff})

            # Check if the username already exists
            if User.objects.filter(username=member.username).exists():
                messages.error(request, f"Username '{member.username}' already exists. Please choose a different username.")
                return render(request, 'members/add_member.html', {'form': form, 'is_staff': request.user.is_staff})

            # Create a user account for the member
            # Disconnect signal to prevent automatic Member creation
            post_save.disconnect(create_member_profile, sender=User)
            user = User.objects.create_user(
                username=member.username,
                email=member.email,
                password=form.cleaned_data['password']
            )
            # Reconnect signal
            post_save.connect(create_member_profile, sender=User)
            member.user = user
            member.save()
            messages.success(request, f"Member '{member.name}' added successfully!")
            return redirect('member_list')
    else:
        form = MemberForm()
    
    return render(request, 'members/add_member.html', {'form': form, 'is_staff': request.user.is_staff})

@login_required
def delete_member(request, member_id):
    """View to delete a member."""
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users to home
    
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        member.delete()
        messages.success(request, f"Member '{member.name}' deleted successfully!")
        return redirect('member_list')
    
    # If not POST, show confirmation page
    return render(request, 'members/delete_member.html', {'member': member, 'is_staff': request.user.is_staff})

@login_required
def edit_member(request, member_id):
    """View to edit an existing member."""
    if not request.user.is_staff:
        messages.error(request, "Only admin users can edit members.")
        return redirect('home')
    
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            updated_member = form.save(commit=False)
            
            # Update the associated User model if username or email changed
            if member.user:
                user = member.user
                user.username = form.cleaned_data['username']
                user.email = form.cleaned_data['email']
                user.save()
            
            updated_member.save()
            messages.success(request, f"Member '{member.name}' updated successfully!")
            return redirect('member_detail', member_id=member.id)
    else:
        # Pre-populate form with existing data
        initial_data = {
            'username': member.username,
            'password': member.password,  # Note: This will show as empty for security
        }
        form = MemberForm(instance=member, initial=initial_data)
    
    return render(request, 'members/edit_member.html', {'form': form, 'member': member, 'is_staff': request.user.is_staff})
