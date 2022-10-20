from django.db import models
import sys
sys.path.append('..')
from login.models import User


class TypeOfCourse(models.Model):
    shortcut = models.CharField(max_length=3)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

class Course(models.Model):
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_by')
    guarantor = models.ForeignKey(User, on_delete=models.CASCADE)
    students_course = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    limit_of_registered = models.IntegerField()
    types_of_courses = models.CharField(max_length=3, choices=types_of_courses_choices, default=COMPULSORY)


class TypeOfCourse(models.Model):
    type_of_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    COMPULSORY = 'C'
    ELECTIVE = 'E'
    COMPULSORY_OPTIONAL = 'C-O'

    types_of_courses_choices = [
        (COMPULSORY, 'Compulsory'),
        (ELECTIVE, 'Elective'),
        (COMPULSORY_OPTIONAL, 'Compulsory-optional'),
    ]


class CourseUpdate(models.Model):
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
