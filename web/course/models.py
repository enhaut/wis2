from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import sys
sys.path.append('..')
from login.models import User


class RegistrationSettingsBase(models.Model):
    class Meta:
        abstract = True

    mandatory = models.BinaryField(default=0)
    capacity = models.IntegerField(null=True)
    opens = models.DateTimeField()
    closes = models.DateTimeField()


class RegistrationSettings(RegistrationSettingsBase):
    pass


class TypeOfCourse(models.Model):
    shortcut = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.shortcut})"


def validate_course_name(value: str):
    if not value.isupper():
        raise ValidationError(
            _('%(value)s has invalid format - only upper characters are allowed.'),
            params={'value': value},
        )


class Course(models.Model):
    shortcut = models.CharField(
        max_length=4,
        primary_key=True,
        validators=[validate_course_name]
    )
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_by', null=True, default=None)
    guarantor = models.ForeignKey(User, on_delete=models.CASCADE)
    type_of_course = models.ForeignKey(TypeOfCourse, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    price = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180)
        ])
    registration = models.ForeignKey(RegistrationSettings, on_delete=models.SET_NULL, null=True, default=None)
    lectors = models.ManyToManyField(User, related_name="teaches")
    students = models.ManyToManyField(User, related_name="have_registred")


class CourseUpdate(models.Model):
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
