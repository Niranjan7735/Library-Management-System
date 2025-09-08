#!/usr/bin/env python3
"""
Test script to verify the borrow book functionality is working correctly
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_mgt.settings')
django.setup()

from books.models import Book
from members.models import Member
from transactions.models import Transaction
from django.utils import timezone

def test_borrow_logic():
    """Test the borrow book logic without HTTP requests"""
    print("Testing borrow book logic...")
    
    # Get available books and active members
    available_books = Book.objects.filter(availability_status=True)
    active_members = Member.objects.filter(status='active')
    
    print(f"Available books: {available_books.count()}")
    print(f"Active members: {active_members.count()}")
    
    if available_books.count() > 0 and active_members.count() > 0:
        book = available_books.first()
        member = active_members.first()
        
        print(f"\nTesting borrow for:")
        print(f"  Book: {book.title} (ID: {book.id}, Available: {book.availability_status})")
        print(f"  Member: {member.name} (ID: {member.id}, Status: {member.status})")
        
        # Simulate the borrow logic from views.py
        try:
            # Check if book is available
            if not book.availability_status:
                print("❌ Book is not available")
                return False
            
            # Check if member is active
            if member.status != 'active':
                print("❌ Member is not active")
                return False
            
            # Create transaction
            transaction = Transaction.objects.create(
                book=book,
                member=member,
                borrow_date=timezone.now().date(),
                status='borrowed'
            )
            
            # Update book availability
            book.availability_status = False
            book.save()
            
            print("✅ Borrow transaction created successfully!")
            print(f"  Transaction ID: {transaction.id}")
            print(f"  Book availability after borrow: {book.availability_status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during borrow: {e}")
            return False
    else:
        print("❌ No available books or active members found for testing")
        return False

if __name__ == "__main__":
    success = test_borrow_logic()
    if success:
        print("\n✅ Borrow functionality test PASSED")
        sys.exit(0)
    else:
        print("\n❌ Borrow functionality test FAILED")
        sys.exit(1)
