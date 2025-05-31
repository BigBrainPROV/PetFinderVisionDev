from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from user_register.models import UserProfile, PetUserProfile


@receiver(post_save, sender=User)
def on_post_save_user_profile(instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        PetUserProfile.objects.get_or_create(user=instance)
