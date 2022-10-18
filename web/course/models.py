from pyexpat import model
from unittest.util import _MAX_LENGTH
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    limit_of_registered = models.IntegerField()
    COMPULSORY = 'C'
    ELECTIVE = 'E'
    COMPULSORY_OPTIONAL = 'C-O'
    course_type_choices = [
        (COMPULSORY, 'Compulsory'),
        (ELECTIVE, 'Elective'),
        (COMPULSORY_OPTIONAL, 'Compulsory-optional'),
    ]
    course_type = models.CharField(max_length=3, choices=course_type_choices, default=COMPULSORY)


class CourseUpdate(models.Model):
    course_update_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.CharField(max_lenght=100)
    date = models.DateTimeField()
    

