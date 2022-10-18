from django.db import models
import sys
sys.path.append('..')
from login.models import User


class Room(models.Model):
    enter_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()