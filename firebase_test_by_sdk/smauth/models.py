from django.db import models


# Create your models here.
class Users(models.Model):
    uid = models.CharField(max_length=30, primary_key=True)
    email = models.CharField(max_length=100, null=True)
    email_verified = models.CharField(max_length=100, null=True)
    password_hash = models.CharField(max_length=100, null=True)
    password_salt = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    photo_url = models.CharField(max_length=100, null=True)
    provider_id = models.CharField(max_length=100, null=True)
    display_name = models.CharField(max_length=100, null=True)
    disabled = models.BooleanField(null=True)
    last_sign_in_timestamp = models.DateTimeField(null=True)
    tokens_valid_after_timestamp = models.DateTimeField(null=True)
    creation_timestamp = models.DateTimeField(null=True)
