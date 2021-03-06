from django.db import models


# Create your models here.
class Users(models.Model):
    uid = models.CharField(max_length=30, primary_key=True)
    email = models.CharField(max_length=100, null=True)
    email_verified = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    photo_url = models.CharField(max_length=100, null=True)
    provider_id = models.CharField(max_length=100, null=True)
    display_name = models.CharField(max_length=100, null=True)
    claims = models.CharField(max_length=255, null=True)
    disabled = models.BooleanField(null=True)
    last_sign_in_timestamp = models.DateTimeField(null=True)
    tokens_valid_after_timestamp = models.DateTimeField(null=True)
    creation_timestamp = models.DateTimeField(null=True)


class Tokens(models.Model):
    uid = models.CharField(max_length=30, primary_key=True)
    id_token = models.CharField(max_length=255, null=True)
    refresh_token = models.CharField(max_length=255, null=True)
    creation_timestamp = models.DateTimeField(null=True)
    expire = models.DateTimeField(null=True)
    expire_in = models.IntegerField(null=True)
    kind = models.CharField(max_length=50, null=True)
