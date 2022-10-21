from django.db import models
import sys
sys.path.append('..')
from login.models import User


class TypeOfCourse(models.Model):
    shortcut = models.CharField(max_length=3)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)


class Course(models.Model):
    type_of_course = models.ForeignKey(TypeOfCourse, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    limit_of_registered = models.IntegerField()
    lectors = models.ManyToManyField(User, related_name="teaches")
    students = models.ManyToManyField(User, related_name="have_registred")


class CourseUpdate(models.Model):
    course_update_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
