# Admin Book Management Testing Steps

## Prerequisites
- Django development server running
- Admin user account with staff privileges
- Existing books in the database (for deletion testing)

## Testing Steps

### 1. Log in to Admin Dashboard
- Navigate to the login page
- Use admin credentials to log in
- Verify redirection to admin dashboard

### 2. Add a New Book
- From admin dashboard, click "Add Book" button
- Fill out the book form with:
  - Title
  - Author
  - ISBN
  - Description
  - Published Date
  - Availability Status
- Submit the form
- Verify success message appears
- Verify redirection to books list
- Confirm new book appears in the list

### 3. Delete a Book
- Navigate to "Books List" from admin dashboard or navigation
- Locate a book to delete
- Click "Delete" button for the selected book
- Confirm deletion in the confirmation page
- Verify success message appears
- Verify redirection to books list
- Confirm book no longer appears in the list

## Files Involved
- `templates/admin_dashboard.html` - Admin dashboard with navigation
- `books/views.py` - Contains add_book() and delete_book() views
- `books/urls.py` - URL routing for book operations
- `templates/books/add_book.html` - Add book form template
- `templates/books/books_list.html` - Books list template
- `templates/books/delete_book.html` - Delete confirmation template

## Expected Behavior
- Only staff users should be able to access add/delete functionality
- Success messages should appear after operations
- Proper redirects should occur after operations
- Books list should update dynamically after operations
