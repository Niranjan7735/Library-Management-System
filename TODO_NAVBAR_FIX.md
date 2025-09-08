# Navbar Fix - Member Details Page

## Problem
When clicking on members details, the user navbar is showing instead of admin navbar.

## Root Cause
The `admin_base.html` template checks `user.is_staff` to determine whether to show admin navbar, but the user object might not be properly available in the template context.

## Solution
Modify `admin_base.html` to use the `is_staff` variable that's already being passed from the view, instead of checking `user.is_staff`.

## Steps to Fix
1. [x] Update `templates/admin_base.html` to use `is_staff` variable instead of `user.is_staff`
2. [ ] Test the changes to ensure correct navbar display

## Files to Modify
- `templates/admin_base.html`
