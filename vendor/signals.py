from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    """
    Signal to handle user-related updates.
    This can be extended to perform additional actions when a user is created or updated.
    """
    pass
