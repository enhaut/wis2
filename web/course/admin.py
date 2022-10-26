from django.shortcuts import render
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect, HttpResponse
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
            courses["all"] = models.Course.objects.filter(
                approved_by__isnull=False
            )
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
        courses.update(self._get_approved_courses(request))

        return courses

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"courses": self._get_courses(request)})


class CreateCourseForm(ModelForm):
    class Meta:
        model = models.Course
        fields = ["type_of_course", "shortcut", "name", "description", "price"]


class CreateCourseView(GroupRequiredMixin, View):
    template_name = "course_create.html"

    group_required = [u"Guarantor", u"Administrator"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"CreateForm": CreateCourseForm()})

    def post(self, request):
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)

            course.guarantor = request.user
            course.save()  # Now you can send it to DB

            return HttpResponseRedirect("/admin/course/" + form.data["shortcut"])

        return render(request, self.template_name, {"CreateForm": form})


class EditCourseView(GroupRequiredMixin, View):
    template_name = "course_edit.html"

    group_required = [u"Guarantor", u"Administrator", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class ApproveCourseView(GroupRequiredMixin, View):
    template_name = "course_edit.html"

    group_required = [u"Administrator"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, id, *args, **kwargs):
        course = {}
        courses = models.Course.objects.get(shortcut=id)
        #courses.approved_by = request.user
        courses.save()
        try:
            course["approved"] = models.Course.objects.filter(
                Q(shortcut=id)
            )
        except ObjectDoesNotExist:
            course["approved"] = []
            return HttpResponse(status=404)

        return HttpResponse(status=204)