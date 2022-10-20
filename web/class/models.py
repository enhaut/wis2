from django.db import models
import sys
sys.path.append('..')

from login.models import User
from course.models import Course


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


class Assessment(models.Model):
    entered_points_by = models.ForeignKey(User)
    class_assessment = models.ForeignKey(Class, on_delete=models.CASCADE)
    point_evaluation = models.IntegerField()
    published_date = models.DateTimeField()


class TypeOfClass(models.Model):
    LECTURE = 'LEC'
    PRACTICE = 'PRA'
    DEMO_PRACTICE = 'DPR'
    EXAM = 'EXM'
    HALF_TERM_EXAM = 'HTX'
    PROJECT = 'PRO'
    CREDIT = 'CRE'

    types_of_classes_choices = [
        (LECTURE, 'Lecture'),
        (PRACTICE, 'Practice'),
        (DEMO_PRACTICE, 'Demo-practice'),
        (EXAM, 'Exam'),
        (HALF_TERM_EXAM, 'Half-term exam'),
        (PROJECT, 'Project'),
        (CREDIT, 'Credit'),
    ]

    types_of_classes = models.CharField(max_length=3, choices=types_of_classes_choices, default=LECTURE)
    type_of_class = models.ForeignKey(Class, on_delete=models.CASCADE)
