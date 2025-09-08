from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    published_date = models.DateField()
    availability_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def update_availability_status(self):
        """Update the availability status based on current borrowed transactions"""
        from transactions.models import Transaction
        borrowed_count = Transaction.objects.filter(book=self, status='borrowed').count()
        # Book is available if there are copies left that are not borrowed
        self.availability_status = borrowed_count < self.quantity
        self.save()

    @property
    def available_quantity(self):
        """Calculate the available quantity (total quantity minus currently borrowed)"""
        from transactions.models import Transaction
        borrowed_count = Transaction.objects.filter(book=self, status='borrowed').count()
        return max(0, self.quantity - borrowed_count)
