from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    username = models.CharField(primary_key=True, unique=True, verbose_name="xlogin", max_length=8)
    email = models.EmailField("mail", unique=True)

    # disable unused default attributes
    id = None
    last_login = None
    is_superuser = None
    groups = None
    user_permissions = None
    is_staff = None
    date_joined = None
    is_active = None

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

