from django.db.models import Q
from django.shortcuts import render
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist


import sys
from . import models
sys.path.append('..')
from course.models import Course


class CoursesView(GroupRequiredMixin, View):
    template_name = "class/admin/courses.html"

    group_required = [u"Guarantor", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_courses(self, request):
        try:
            courses = Course.objects.filter(
                Q(lectors=request.user) | Q(guarantor=request.user)
            )
        except ObjectDoesNotExist:
            return []

        return courses

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"courses": self._get_courses(request)})


class ClassView(GroupRequiredMixin, View):
    template_name = "class/admin/classes.html"

    group_required = [u"Guarantor", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_classes(self, request, id):
        try:
            classes = models.Class.objects.filter(
                courses_class=id
            )
        except ObjectDoesNotExist:
            return []

        return classes

    def get(self, request, id, *args, **kwargs):
        return render(request, self.template_name, {"classes": self._get_classes(request, id)})

