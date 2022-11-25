from django.db import models
from django.core.exceptions import ValidationError
from django.utils.regex_helper import _lazy_re_compile
from django.core.validators import RegexValidator
import sys
sys.path.append('..')
from login.models import User


class Room(models.Model):
    enter_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    shortcut = models.CharField(
        max_length=50,
        validators=[
            RegexValidator('^[A-Z]+[0-9]*$', message='First char must be capital letter, rest must be numeric')
        ]
    )

    def __str__(self):
        return f"{self.shortcut} (capacity: {self.capacity})"
