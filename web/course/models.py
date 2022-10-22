from django.db import models
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
    shortcut = models.CharField(max_length=3)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)


class Course(models.Model):
    shortcut = models.CharField(max_length=3, primary_key=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_by')
    guarantor = models.ForeignKey(User, on_delete=models.CASCADE)
    type_of_course = models.ForeignKey(TypeOfCourse, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    registration = models.ForeignKey(RegistrationSettings, on_delete=models.SET_NULL, null=True)
    lectors = models.ManyToManyField(User, related_name="teaches")
    students = models.ManyToManyField(User, related_name="have_registred")


class CourseUpdate(models.Model):
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
