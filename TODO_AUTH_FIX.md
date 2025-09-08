# Authentication Fix - Admin Dashboard Access Control

## Problem
When admin users logged in, they were seeing both the admin dashboard and user dashboard content. The system was treating admin users as both admin and regular users.

## Changes Made

### 1. Modified `library_mgt/views.py`
- **custom_login function**: Updated to redirect admin users to admin dashboard and regular users to home page
- **home function**: Added redirection logic to redirect admin users to admin dashboard

### 2. Modified `templates/home.html`
- Reverted the conditional check to show content for all authenticated users (redirection is now handled in the view)

## Files Updated
- [x] `library_mgt/views.py` - Updated login redirection logic
- [x] `templates/home.html` - Reverted conditional check

## Expected Behavior
- **Admin users**: After login, redirected directly to admin dashboard (`/admin-dashboard/`)
- **Regular users**: After login, see the user dashboard (`/home/`)
- **Anonymous users**: See the public landing page with login/register options

## Testing Required
1. Test login with admin account - should redirect to admin dashboard
2. Test login with regular user account - should show user dashboard
3. Test access to admin dashboard with regular user - should redirect to home
4. Test access to home page with admin user - should redirect to admin dashboard

## Notes
- The admin dashboard already had proper access control to prevent non-admin users from accessing it
- The login view now properly distinguishes between admin and regular users for redirection
