"""
Contains all signals relating to the AAC Admin component
"""
from django.dispatch import receiver
from django.db.models.signals import post_save
from makeReports.models import (
    Profile,
    User
)

@receiver(post_save,sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    """
    Updates the custom profile when users are created
    
    Args:
        sender (type): model type sending hook
        instance (User): user updated
        created (bool): whether model was newly created
    """
    #this updates profile when user is updated
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()