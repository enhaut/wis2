from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from . import models
import importlib
Class = importlib.import_module("class.models", "Class")
RegistrationToClass = importlib.import_module("class.models", "RegistrationToClass")



class RegistrationOverviewView(GroupRequiredMixin, View):
    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    template_name = "course/registrations.html"

    def _get_courses(self, request):
        ordered_courses = {"opened": [], "closed": []}

        courses = models.Course.objects.filter(
            ~Q(
                registration=None
            )
        )
        now = timezone.now()

        for course in courses:
            if request.user in course.students.all():
                continue  # skip if already registered

            if course.registration and course.registration.opens < now < course.registration.closes:
                ordered_courses["opened"].append(course)
            else:
                ordered_courses["closed"].append(course)

        return ordered_courses

    def get(self, request):
        return render(request, self.template_name, self._get_courses(request))


class RegistrationView(GroupRequiredMixin, View):
    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    template_name = "course/registration_status.html"

    def _register_user_to_course(self, user, course):
        try:
            registration = models.RegistrationToCourse.objects.get(user=user, course_id=course)
        except ObjectDoesNotExist:
            registration = None

        if registration is not None:
            return "Už si zaregistrovaný"

        msg = "Registrovaný :)"
        registration = models.RegistrationToCourse(user=user, course_id=course)
        if course.registration.auto_approve:
            registration.accepted = True
        else:
            registration.accepted = False
            msg = "Registrovaný, ale tvoju registráciu ešte musí schváliť garant predmetu alebo učiteľ"

        registration.save()

        return msg

    def _register_course(self, request, subject):
        try:
            course = models.Course.objects.get(shortcut=subject)
        except ObjectDoesNotExist:
            return "Požadovaný kurz nebol nájdený"

        now = timezone.now()

        if (registration := course.registration) and registration.opens < now < registration.closes:
            if registration.capacity > course.students.count():
                return self._register_user_to_course(request.user, course)
            else:
                return "V tomto kurze už nie je voľné miesto"
        else:
            return "Registrácia je zatvorená"

    def get(self, request, subject):
        return render(request, self.template_name, {"msg": self._register_course(request, subject), "subject": subject})
class StudentCourseView(GroupRequiredMixin, View):
    template_name = "course.html"

    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            students_courses = models.RegistrationToCourse.objects.filter(user=request.user)
            all_courses = models.Course.objects.filter(approved_by="lampa")
            return render(request, 'course.html', {'students_courses' : students_courses, 'all_courses' : all_courses})

class MyCourseView(GroupRequiredMixin, View):
    template_name = "course_enrolled.html"

    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        students_courses = models.RegistrationToCourse.objects.filter(user=request.user)
        points = {}
        for course in students_courses:
            classes = Class.Class.objects.filter(course=course.course_id)
            assessments = Class.Assessment.objects.filter(student=request.user, evaluated_class__in=classes)
            points[course.course_id.shortcut] = sum(assessment.point_evaluation for assessment in assessments)
        if request.user.is_authenticated:
            return render(request, 'course_enrolled.html', {'students_courses' : students_courses, 'points' : points})

class MyEnrolledCourseView(GroupRequiredMixin, View):
    template_name = "my_enrolled_course.html"

    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_classes(self, request, shortcut, *args, **kwargs):
        classes = []

        course = models.RegistrationToCourse.objects.get(accepted=True, user=request.user, course_id=shortcut)

        course_classes = Class.Class.objects.filter(course=course.course_id)
        registrations = RegistrationToClass.RegistrationToClass.objects.filter(class_id__in=course_classes, user=request.user, accepted=True)
        for registration in registrations:
            classes.append(registration.class_id)
        return classes

    def get(self, request, shortcut, *args, **kwargs):
        if request.user.is_authenticated:
            course = models.Course.objects.get(shortcut=shortcut)
            updates = models.CourseUpdate.objects.filter(course_id=shortcut)
            return render(request, "my_enrolled_course.html", {'course' : course, 'updates' : updates, 'classes' : self._get_classes(request, shortcut)})


class TimetableView(GroupRequiredMixin, View):
    template_name = "timetable.html"

    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username = request.user
            return render(request, "timetable.html", {"username" : username})