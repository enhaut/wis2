from django.shortcuts import render
from django.db.models import Q
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from . import models


class CourseAdminView(GroupRequiredMixin, View):
    template_name = "course_admin.html"

    group_required = [u"Guarantor", u"Administrator", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_teached_courser(self, request):
        courses = {}
        try:
            courses["guaranted"] = models.Course.objects.filter(
                Q(guarantor=request.user)
            )
        except ObjectDoesNotExist:
            courses["guaranted"] = []

        courses["teached"] = []  # TODO: teacher

        return courses

    def _get_approved_courses(self, request):
        courses = {}

        try:
            courses["all"] = models.Course.objects.all()
        except ObjectDoesNotExist:
            courses["all"] = []

        try:
            courses["to_approve"] = models.Course.objects.filter(
                Q(approved_by=None)
            )
        except ObjectDoesNotExist:
            courses["to_approve"] = []

        return courses

    def _get_courses(self, request):
        courses = {}
        courses.update(self._get_teached_courser(request))

        return courses

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"courses": self._get_courses(request)})


