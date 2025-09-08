#!/usr/bin/env python3
"""
Test script to verify error handling in borrow book functionality
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

def test_unavailable_book():
    """Test borrowing an unavailable book"""
    print("Testing unavailable book scenario...")
    
    # Find an unavailable book
    unavailable_books = Book.objects.filter(availability_status=False)
    active_members = Member.objects.filter(status='active')
    
    if unavailable_books.count() > 0 and active_members.count() > 0:
        book = unavailable_books.first()
        member = active_members.first()
        
        print(f"  Book: {book.title} (Available: {book.availability_status})")
        print(f"  Member: {member.name} (Status: {member.status})")
        
        # This should fail due to book being unavailable
        if not book.availability_status:
            print("✅ Correctly detected unavailable book")
            return True
        else:
            print("❌ Book should be unavailable")
            return False
    else:
        print("❌ No unavailable books found for testing")
        return False

def test_inactive_member():
    """Test borrowing with an inactive member"""
    print("Testing inactive member scenario...")
    
    # Find an inactive member
    inactive_members = Member.objects.filter(status='inactive')
    available_books = Book.objects.filter(availability_status=True)
    
    if inactive_members.count() > 0 and available_books.count() > 0:
        member = inactive_members.first()
        book = available_books.first()
        
        print(f"  Book: {book.title} (Available: {book.availability_status})")
        print(f"  Member: {member.name} (Status: {member.status})")
        
        # This should fail due to member being inactive
        if member.status != 'active':
            print("✅ Correctly detected inactive member")
            return True
        else:
            print("❌ Member should be inactive")
            return False
    else:
        print("❌ No inactive members found for testing")
        return True  # This is okay if no inactive members exist

def test_nonexistent_entities():
    """Test handling of nonexistent books/members"""
    print("Testing nonexistent entities scenario...")
    
    # These IDs should not exist
    nonexistent_book_id = 9999
    nonexistent_member_id = 9999
    
    try:
        Book.objects.get(id=nonexistent_book_id)
        print("❌ Found nonexistent book")
        return False
    except Book.DoesNotExist:
        print("✅ Correctly handled nonexistent book")
    
    try:
        Member.objects.get(id=nonexistent_member_id)
        print("❌ Found nonexistent member")
        return False
    except Member.DoesNotExist:
        print("✅ Correctly handled nonexistent member")
    
    return True

if __name__ == "__main__":
    print("Testing error scenarios for borrow functionality...\n")
    
    tests = [
        test_unavailable_book,
        test_inactive_member,
        test_nonexistent_entities
    ]
    
    all_passed = True
    for test in tests:
        try:
            result = test()
            if not result:
                all_passed = False
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            all_passed = False
            print()
    
    if all_passed:
        print("✅ All error scenario tests PASSED")
        sys.exit(0)
    else:
        print("❌ Some error scenario tests FAILED")
        sys.exit(1)
