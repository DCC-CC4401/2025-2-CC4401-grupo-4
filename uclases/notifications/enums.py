from django.db import models

class NotificationTypes(models.TextChoices):
    INSCRIPTION_ACCEPTED = 'inscription_accepted', 'Inscription Accepted'
