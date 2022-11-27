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

    mandatory = models.BooleanField(default=False)
    auto_approve = models.BooleanField(default=True)
    capacity = models.IntegerField(null=True)
    opens = models.DateTimeField()
    closes = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.opens > self.closes:
            raise ValidationError("Invalid date range!")

        super().save(*args, **kwargs)


class RegistrationSettings(RegistrationSettingsBase):
    pass


class TypeOfCourse(models.Model):
    shortcut = models.CharField(max_length=7, primary_key=True)
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=256)

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
    students = models.ManyToManyField(User, related_name="have_registred", through="RegistrationToCourse")

    def __str__(self):
        return f"{self.shortcut} ({self.name})"


class RegistrationToCourse(models.Model):
    accepted = models.BooleanField(default=1)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("course_id", "user"), )


class CourseUpdate(models.Model):
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    date = models.DateTimeField()

    class Meta:
        ordering = ["-date"]
