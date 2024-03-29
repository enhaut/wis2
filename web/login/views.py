from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import logout
from django.utils import timezone
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from django.contrib.auth.models import Group
from django import forms
import sys
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import importlib
from . import basic_auth as auth
from datetime import datetime, timedelta
from course.models import Course
from course.models import CourseUpdate
from . import models
Class = importlib.import_module("class.models", "Class")


class LoginPageView(View):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class LoginView(View):
    @auth.logged_in_or_basicauth()
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/overview')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)

        location = request.scheme + "://log:out@" + request.get_host()
        res = HttpResponse(location, status=302)
        res['Location'] = location

        return res


class AvailableCoursesView(View):
    redirect_unauthenticated_users = False
    raise_exception = True

    template_name = "courses_available.html"

    def _get_courses(self, request):
        ordered_courses = {"opened": [], "closed": []}

        courses = Course.objects.filter(
            ~Q(
                registration=None
            )
        )
        now = timezone.now()

        for course in courses:
            if course.registration and course.registration.opens < now < course.registration.closes:
                ordered_courses["opened"].append(course)
            else:
                ordered_courses["closed"].append(course)

        return ordered_courses

    def get(self, request):
        return render(request, self.template_name, self._get_courses(request))


class CourseContentView(View):
    template_name = "course_content.html"

    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, shortcut, *args, **kwargs):
        course = Course.objects.get(shortcut=shortcut)
        updates = CourseUpdate.objects.filter(course_id=shortcut)
        return render(request, "course_content.html", {'course': course, 'updates': updates})


class EditUserForm(ModelForm):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name"]


class EditPwForm(ModelForm):
    class Meta:
        model = models.User
        fields = ["password"]


class EditProfileView(GroupRequiredMixin, View):
    template_name = "user_edit.html"

    group_required = [u"Student", u"Administrator", u"Guarantor", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, edit_profile=None, edit_pw=None, *args, **kwargs):
        if not (user := request.user):
            return HttpResponseNotFound(f"User could not be found!")

        if not edit_profile:
            edit_profile = EditUserForm(
                initial={
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            )

        if not edit_pw:
            edit_pw = EditPwForm(
                initial={
                }
            )

            return render(
                request,
                self.template_name,
                {
                    "user": user,
                    "EditUserForm": edit_profile,
                    "EditPwForm": edit_pw
                }
            )

    def _process_create_user_form(self, request):
        form = EditUserForm(request.POST)
        try:
            user = models.User.objects.get(
                Q(username=request.user.username)
            )
        except ObjectDoesNotExist:
            user = None

        if form.data["first_name"]:
            if not form.data["first_name"].isalpha():
                return HttpResponseNotFound(f"First name must contains letters only!")
            else:
                user.first_name = form.data["first_name"]
                request.user.first_name = form.data["first_name"]
        if form.data["last_name"]:
            if not form.data["last_name"].isalpha():
                raise ValidationError("Last name must contains letters only!")
            else:
                user.last_name = form.data["last_name"]
                request.user.last_name = form.data["last_name"]
        user.save()

        form = EditUserForm(initial={
                "first_name": form.data["first_name"],
                "last_name": form.data["last_name"]
            })
        return self.get(request, edit_profile=form)

    def _process_edit_pw_form(self, request):
        form = EditPwForm(request.POST)
        try:
            user = models.User.objects.get(
                Q(username=request.user.username)
            )
        except ObjectDoesNotExist:
            user = None

        if form.data["password"]:
            user.set_password(form.data["password"])
        user.save()

        if form.data["password"]:
            return redirect("loginpage")

        form = EditPwForm(initial={
            "password": form.data["password"]
        })

        return self.get(request, )

    def post(self, request, *args, **kwargs):
        if "form" in request.POST:
            match request.POST["form"]:
                case "edit_profile":
                    return self._process_create_user_form(request)
                case "edit_pw":
                    return self._process_edit_pw_form(request)

        return self.get(request)



class AddUserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["username", "email", "first_name", "last_name", "password"]

class RemoveUserForm(forms.Form):
    student = forms.CharField(label="username")

class UserManagementView(GroupRequiredMixin, View):
    template_name = "user_management.html"

    group_required = [u"Administrator"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _process_add_user_form(self, request):
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = models.User()
            user.username = form.data['username']
            user.email = form.data['email']
            user.first_name = form.data['first_name']
            user.last_name = form.data['last_name']
            user.set_password(form.data['password'])
            user.save()

            stud = Group.objects.get(name='Student')
            user.groups.add(stud)
            user.save()

            return self.get(request)

    def _process_remove_user_form(self, request):
        form = RemoveUserForm(request.POST)
        user = models.User.objects.get(username=form.data['username'])
        user.delete()

        return self.get(request)

    def post(self, request):
        if "form" in request.POST:
            match request.POST["form"]:
                case "add_user":
                    return self._process_add_user_form(request)
                case "remove_user":
                    return self._process_remove_user_form(request)
        return self.get(request)

    def get(self, request, add_form=AddUserForm()):
        students = models.User.objects.all()
        return render(request, self.template_name, {'form' : add_form, 'students' : students})