#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_mgt.settings')
django.setup()

from members.models import Member
from django.contrib.auth.models import User

def assign_temp_user_to_members():
    try:
        temp_user = User.objects.get(username='temp_user')
        members = Member.objects.all()
        
        for member in members:
            member.user = temp_user
            member.save()
            print(f'Assigned temp user to {member.name}')
        
        print(f'Successfully assigned temp user to {members.count()} members.')
        
    except User.DoesNotExist:
        print("Temporary user 'temp_user' does not exist. Please create it first.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    assign_temp_user_to_members()
