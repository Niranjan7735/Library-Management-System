#!/usr/bin/env python
"""
Migration-safe script to create Member profiles for all existing users
who don't have a Member profile yet.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_mgt.settings')
django.setup()

from django.contrib.auth.models import User
from members.models import Member

def create_missing_member_profiles():
    """Create Member profiles for users who don't have one"""
    users_without_members = User.objects.filter(member__isnull=True)
    
    print(f"Found {users_without_members.count()} users without Member profiles")
    
    created_count = 0
    for user in users_without_members:
        # Check if user already has a member (double-check)
        if not hasattr(user, 'member'):
            try:
                # Create Member with user data
                Member.objects.create(
                    user=user,
                    name=user.username,
                    email=user.email or f"{user.username}@example.com",
                    phone="",
                    address="",
                    status="active"
                )
                created_count += 1
                print(f"✓ Created Member profile for user: {user.username}")
            except Exception as e:
                print(f"✗ Error creating Member for {user.username}: {e}")
    
    print(f"\nSuccessfully created {created_count} Member profiles")
    return created_count

if __name__ == "__main__":
    print("Creating Member profiles for existing users...")
    create_missing_member_profiles()
