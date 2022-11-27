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
from django.shortcuts import redirect

from datetime import datetime
from django.utils.timezone import make_aware, get_current_timezone

import sys
sys.path.append('..')
from login.models import User
import importlib
Class = importlib.import_module("class.models", "Class")
from . import models


class CourseAdminView(GroupRequiredMixin, View):
    template_name = "course_admin.html"

    group_required = [u"Guarantor", u"Administrator", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_teached_courser(self, request):
        courses = {"guaranted": [], "teached": []}
        try:
            courses["guaranted"] = models.Course.objects.filter(
                Q(guarantor=request.user)
            )
        except ObjectDoesNotExist:
            pass

        try:
            courses["teached"] = models.Course.objects.filter(
                Q(lectors=request.user)
            )
        except ObjectDoesNotExist:
            pass

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


class CreateCourseUpdateForm(ModelForm):
    class Meta:
        model = models.CourseUpdate
        fields = ["title", "date", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "value": "Update #"
                }
            ),
            "date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "value": datetime.now().strftime("%Y-%m-%dT%H:%M")  #"2018-06-12T19:30"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "HTML input is supported"
                }
            )
        }


class EditCourseForm(ModelForm):
    class Meta:
        model = models.Course
        fields = ["name", "type_of_course", "description", "price"]


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

    group_required = [u"Guarantor", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_course(self, id, request):
        try:
            return models.Course.objects.filter(
                Q(
                    shortcut=id,
                    guarantor=request.user
                ) | Q(
                    shortcut=id,
                    lectors=request.user
                )
            )[0]
        except (ObjectDoesNotExist, KeyError, IndexError):
            return []

    def _get_updates(self, course: models.Course):
        try:
            return models.CourseUpdate.objects.filter(
                course=course
            )
        except ObjectDoesNotExist:
            return []

    def _get_students_points(self, course: models.Course):
        points = {}
        for student in course.students.all():
            try:
                models.RegistrationToCourse.objects.get(course_id=course, user=student, accepted=True)
            except ObjectDoesNotExist:
                points[student.username] = None
                continue

            points[student.username] = 0
            try:
                classes = Class.Class.objects.filter(course=course)
                assessments = Class.Assessment.objects.filter(student=student, evaluated_class__in=classes)
            except ObjectDoesNotExist:
                continue

            points[student.username] = sum(assessment.point_evaluation for assessment in assessments)

        return points

    def get(self, request, id, add_lector=AddLectorForm(), add_update=CreateCourseUpdateForm(), edit_course=None, *args, **kwargs):
        if not (course := self._get_course(id)):
            return HttpResponseNotFound(f"Course {id} could not be found!")

        if not edit_course:
            edit_course = EditCourseForm(
                initial={
                    "name": course.name,
                    "type_of_course": course.type_of_course,
                    "description": course.description,
                    "price": course.price
                }
            )

        return render(
            request,
            self.template_name,
            {
                "course": course,
                "points": self._get_students_points(course),
                "updates": self._get_updates(course),
                "form": add_lector,
                "CreateUpdateForm": add_update,
                "EditCourseForm": edit_course
            }
        )

    def _process_add_lector_form(self, request, id):
        form = AddLectorForm(request.POST)
        if form.is_valid():
            try:
                course = models.Course.objects.get(
                    Q(
                    shortcut=id,
                    guarantor=request.user
                ) | Q(
                    shortcut=id,
                    lectors=request.user
                ))
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

            if not self._get_course(id, request):
                return HttpResponseNotFound(f"Course {id} could not be found!")

            course = models.Course.objects.get(shortcut=id, lectors=user)
            course.lectors.remove(user)
            course.save()

        return self.get(request, id)

    def _process_add_update_form(self, request, id):
        form = CreateCourseUpdateForm(request.POST)

        try:
            course = models.Course.objects.filter(
                Q(shortcut=id, lectors=request.user) | Q(shortcut=id, guarantor=request.user)
            )
        except ObjectDoesNotExist:
            form.add_error("description", "You are not teacher/guarantor")
            course = None

        if form.is_valid() and course:
            update = form.save(commit=False)
            update.published_by = request.user
            update.course = course[0]
            update.save()

            form = CreateCourseUpdateForm()

        return self.get(request, id, add_update=form)

    def _process_edit_course_form(self, request, id):
        form = EditCourseForm(request.POST)
        if not self._get_course(id, request):
            return HttpResponseNotFound(f"Course {id} could not be found!")

        try:
            course = models.Course.objects.filter(
                Q(shortcut=id, guarantor=request.user)
            )
            form = EditCourseForm(request.POST, instance=course[0])
        except ObjectDoesNotExist:
            form.add_error("title", "You are not guarantor")
            course = None

        if form.is_valid() and course:
            form.save()

            form = CreateCourseUpdateForm()

        return self.get(request, id, edit_course=form)

    def post(self, request, id, *args, **kwargs):
        if "form" in request.POST:
            match request.POST["form"]:
                case "add_lector":
                    return self._process_add_lector_form(request, id)
                case "remove_lector":
                    return self._process_remove_lector_form(request, id)
                case "add_update":
                    self._process_add_update_form(request, id)
                case "edit_course":
                    self._process_edit_course_form(request, id)

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


class RegistrationForm(ModelForm):
    class Meta:
        model = models.RegistrationSettings
        fields = ["opens", "closes", "mandatory", "auto_approve", "capacity"]
        widgets = {
            "opens": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "value": datetime.now().strftime("%Y-%m-%dT%H:%M")
                }
            ),
            "closes": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "value": datetime.now().strftime("%Y-%m-%dT%H:%M")
                }
            ),
            "capacity": forms.NumberInput(
                attrs={
                    "min": 0
                }
            )
        }


class RegistrationSettingsViewBase(GroupRequiredMixin, View):
    group_required = [u"Guarantor"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_form_values(self, unit):
        if unit.registration:
            return {
                "opens": unit.registration.opens,
                "closes": unit.registration.closes,
                "mandatory": unit.registration.mandatory,
                "auto_approve": unit.registration.auto_approve,
                "capacity": unit.registration.capacity,
            }
        else:
            return {
                "opens": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "closes": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

    @staticmethod
    def _process_registration_form(form, unit):
        if not form.is_valid():
            return None

        if not unit.registration:
            registration = form.save()
        else:
            registration = unit.registration
            registration.mandatory = form.data.get("mandatory", False) is not False
            registration.auto_approve = form.data.get("auto_approve", False) is not False
            registration.capacity = int(form.data["capacity"])
            registration.opens = make_aware(
                datetime.strptime(form.data["opens"], "%Y-%m-%dT%H:%M"),
                get_current_timezone(),
                False
            )

            registration.closes = make_aware(
                datetime.strptime(form.data["closes"], "%Y-%m-%dT%H:%M"),
                get_current_timezone(),
                False
            )
            try:
                registration.save()
            except ValidationError:
                form.add_error("closes", "Invalid date range")

        if not form.errors:
            unit.registration = registration
            unit.save()
            form = None  # data will be set by get method

        return form


class RegistrationSettingsView(RegistrationSettingsViewBase):
    template_name = "course/registration.html"

    @staticmethod
    def _get_course(request, id):
        try:
            return models.Course.objects.get(
                shortcut=id,
                guarantor=request.user
            )
        except ObjectDoesNotExist:
            return None

    def get(self, request, id, form=None, *args, **kwargs):
        if not (course := self._get_course(request, id)):
            return HttpResponseNotFound(f"Course {id} could not be found!")

        if form is None:
            form = RegistrationForm(
                initial=self._get_form_values(course)
            )

        return render(
            request,
            self.template_name,
            {
                "RegistrationForm": form,
                "course": course
            }
        )

    def post(self, request, id):
        form = RegistrationForm(request.POST)

        if not (course := self._get_course(request, id)):
            return HttpResponseNotFound(f"Course {id} could not be found!")

        form = self._process_registration_form(form, course)

        return self.get(request, id, form)


class ApproveRegistrationView(GroupRequiredMixin, View):
    group_required = [u"Guarantor"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, id, user, *args, **kwargs):
        try:
            models.Course.objects.get(shortcut=id, guarantor=request.user)
            user = models.User.objects.get(username=user)
            registration = models.RegistrationToCourse.objects.get(course_id=id, user=user, accepted=False)
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        registration.accepted = True
        registration.save()

        return redirect("edit_course", id=id)
