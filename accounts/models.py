from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import os
from random import randrange
from django.urls import reverse
from django import template

register = template.Library()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_email = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

