from django.db import models
import sys
sys.path.append('..')
from login.models import User


class Course(models.Model):
    students_course = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    limit_of_registered = models.IntegerField()



class CourseUpdate(models.Model):
    course_update_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()

class TypeOfCourse(models.Model):
    COMPULSORY = 'C'
    ELECTIVE = 'E'
    COMPULSORY_OPTIONAL = 'C-O'

    types_of_courses_choices = [
        (COMPULSORY, 'Compulsory'),
        (ELECTIVE, 'Elective'),
        (COMPULSORY_OPTIONAL, 'Compulsory-optional'),
    ]


    types_of_courses = models.CharField(max_length=3, choices=types_of_courses_choices, default=COMPULSORY)
    type_of_course = models.ForeignKey(Course, on_delete=models.CASCADE)



    

