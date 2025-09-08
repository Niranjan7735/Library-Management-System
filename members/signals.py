from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Member

@receiver(post_save, sender=User)
def create_member_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Member profile when a new User is created
    """
    if created:
        # Create Member with default values
        Member.objects.create(
            user=instance,
            name=instance.username,
            email=instance.email,
            phone="",  # Default empty phone
            address="",  # Default empty address
            membership_date=timezone.now().date(),
            status="active"
        )
