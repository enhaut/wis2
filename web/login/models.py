from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    username = models.CharField(primary_key=True, unique=True, verbose_name="xlogin", max_length=8)
    email = models.EmailField("mail", unique=True)

    ROLES = [
        ("R", "Registred user"),
        ("S", "Student"),
        ("T", "Teacher"),
        ("G", "Guarantor"),
        ("A", "Administrator")
    ]
    role = models.CharField(max_length=1, choices=ROLES, default=ROLES[0][0])

    # disable unused default attributes
    id = None
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

