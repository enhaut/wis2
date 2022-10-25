from django.shortcuts import render
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import sys
sys.path.append('..')
from login.models import User
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


def validate_lector_exists(login):
    try:
        User.objects.get(pk=login)
    except ObjectDoesNotExist:
        raise ValidationError(
            _(f'{login} does not exist')
        )


def validate_lector_group(login):
    try:
        user_data = User.objects.get(pk=login)
    except ObjectDoesNotExist:
        return

    try:
        if not user_data.groups.filter(Q(name="Teacher") | Q(name="Guarantor")):
            raise ObjectDoesNotExist()

    except ObjectDoesNotExist:
        raise ValidationError(
            _(f'{login} is not Teacher or Guarantor')
        )


class AddLectorForm(forms.Form):
    lector = forms.CharField(
        label='lector',
        max_length=8,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'xlogin00',
                "style": "width: 5em"
            }
        ),
        validators=[
            validate_lector_exists,
            validate_lector_group
        ]
    )


class RemoveLectorForm(forms.Form):
    lector = forms.CharField(
        label='lector',
        max_length=8,
        validators=[
            validate_lector_exists,
        ]
    )


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

    def _get_course(self, id):
        try:
            return models.Course.objects.filter(
                shortcut=id
            )[0]
        except (ObjectDoesNotExist, KeyError, IndexError):
            return []

    def get(self, request, id, add_lector=AddLectorForm(), *args, **kwargs):
        if not (course := self._get_course(id)):
            return HttpResponseNotFound(f"Course {id} could not be found!")

        return render(request, self.template_name, {"course": course, "form": add_lector})

    def _process_add_lector_form(self, request, id):
        form = AddLectorForm(request.POST)
        if form.is_valid():
            try:
                course = models.Course.objects.get(shortcut=id)
            except ObjectDoesNotExist:
                return HttpResponseNotFound(f"Course {id} could not be found!")

            user = User.objects.get(username=form.data["lector"])
            if user not in course.lectors.all():
                course.lectors.add(user)
                course.save()
                form = AddLectorForm()
            else:
                form.add_error("lector", f"User {user.username} is already teacher for this class")

        return self.get(request, id, form)

    def _process_remove_lector_form(self, request, id):
        form = RemoveLectorForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=form.data["lector"])

            course = models.Course.objects.get(shortcut=id, lectors=user)
            course.lectors.remove(user)
            course.save()

        return self.get(request, id)

    def post(self, request, id, *args, **kwargs):
        if "form" in request.POST:
            match request.POST["form"]:
                case "add_lector":
                    return self._process_add_lector_form(request, id)
                case "remove_lector":
                    return self._process_remove_lector_form(request, id)

        return self.get(request, id)


class ApproveCourseView(GroupRequiredMixin, View):
    template_name = "course_edit.html"

    group_required = [u"Administrator"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, id, *args, **kwargs):
        course = {}
        courses = models.Course.objects.get(shortcut=id)
        courses.approved_by = request.user
        courses.save()
        try:
            course["approved"] = models.Course.objects.filter(
                Q(shortcut=id)
            )
        except ObjectDoesNotExist:
            course["approved"] = []
            return HttpResponse(status=404)

        return HttpResponse(status=204)