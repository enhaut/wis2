from pyexpat import model
from unittest.util import _MAX_LENGTH
from django.db import models
import sys
sys.path.append('..')
from login.models import User


class Course(models.Model):
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_by')
    parameters_set_by = models.ForeignKey(User, on_delete=models.CASCADE)
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
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
    

