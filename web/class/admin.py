from django import forms
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist


from datetime import datetime, timedelta
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


class CreateClassForm(forms.ModelForm):
    class Meta:
        model = models.Class
        fields = ["type_of_class", "name", "description", "date_from", "date_to"]
        widgets = {
            "date_from": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "value": datetime.now().strftime("%Y-%m-%dT%H:%M")  # "2018-06-12T19:30"
                }
            ),
            "date_to": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "value": (datetime.now() + timedelta(hours=1, minutes=50)).strftime("%Y-%m-%dT%H:%M")
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "HTML input is supported"
                }
            )
        }


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

    def get(self, request, id, create_form=None, *args, **kwargs):
        try:
            Course.objects.get(
                Q(shortcut=id, lectors=request.user) | Q(shortcut=id, guarantor=request.user)
            )
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        if not create_form:
            create_form = CreateClassForm()

        return render(
            request,
            self.template_name,
            {
                "classes": self._get_classes(request, id),
                "CreateClassForm": create_form
            }
        )

    def post(self, request, id):
        form = CreateClassForm(request.POST)
        try:
            course = Course.objects.get(
                Q(shortcut=id, lectors=request.user) | Q(shortcut=id, guarantor=request.user)
            )
        except ObjectDoesNotExist:
            return HttpResponse(status=400)

        if form.data["date_to"] < form.data["date_from"]:
            form.add_error("date_to", "Date to needs to be bigger than date from")
            return self.get(request, id, create_form=form)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.courses_class = course

            obj.save()
            form = CreateClassForm()

        return self.get(request, id, create_form=form)


