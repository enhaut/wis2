from django.db import models
import sys
sys.path.append('..')
from course.models import Course
from room.models import Room
from login.models import User


class TypeOfClass(models.Model):
    shortcut = models.CharField(max_length=3)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)


class Class(models.Model):
    courses_class = models.ForeignKey(Course, on_delete=models.CASCADE)
    type_of_class = models.ForeignKey(TypeOfClass, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
    mandatory_registration = models.BinaryField()
    rooms = models.ManyToManyField(Room)
    students = models.ManyToManyField(User)


class Assessment(models.Model):
    entered_points_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    class_assessment = models.ForeignKey(Class, on_delete=models.RESTRICT)
    point_evaluation = models.FloatField()
    published_date = models.DateTimeField()
    student = models.ForeignKey(User, on_delete=models.CASCADE)
