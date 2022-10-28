from django.db import models
from django.core.exceptions import ValidationError
import sys
sys.path.append('..')
from course.models import Course, RegistrationSettingsBase
from room.models import Room
from login.models import User


class RegistrationSettings(RegistrationSettingsBase):
    pass


class TypeOfClass(models.Model):
    shortcut = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Class(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    type = models.ForeignKey(TypeOfClass, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=10_000)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    registration = models.ForeignKey(RegistrationSettings, on_delete=models.SET_NULL, null=True)
    rooms = models.ManyToManyField(Room)
    students = models.ManyToManyField(User, through="RegistrationToClass")

    def __str__(self):
        return f"{self.course.shortcut}/{self.name}"

    def save(self, *args, **kwargs):
        if self.date_from > self.date_to:
            raise ValidationError("Date to cannot be bigger than date from!")

        super().save(*args, **kwargs)


class RegistrationToClass(models.Model):
    accepted = models.BooleanField(default=1)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("class_id", "user"), )


class Assessment(models.Model):
    entered_points_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="evaluates", null=True)
    evaluated_class = models.ForeignKey(Class, on_delete=models.RESTRICT)
    point_evaluation = models.FloatField()
    published_date = models.DateTimeField()
    student = models.ForeignKey(User, on_delete=models.CASCADE)
