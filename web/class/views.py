from django.shortcuts import render
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.db.utils import IntegrityError

from django.utils import timezone

import sys
sys.path.append('..')
from course.models import RegistrationToCourse

from . import models


class ClassRegistrationForm(forms.Form):
    class_id = forms.IntegerField()
    course_id = forms.CharField()


class ClassesRegistrationView(GroupRequiredMixin, View):
    template_name = "class/registration_overview.html"

    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_classes(self, request):
        classes = []

        courses = RegistrationToCourse.objects.filter(accepted=True, user=request.user)

        for course in courses.all():
            course_classes = models.Class.objects.filter(course=course.course_id)
            for course_class in course_classes:
                registration = models.RegistrationToClass.objects.filter(
                    class_id=course_class,
                    user=request.user
                )
                if registration.all():
                    continue  # already registered TODO: cancel registration
                classes.append(course_class)

        return classes

    def get(self, request, *args, **kwargs):
        return render(
            request, self.template_name, {
                "classes": self._get_classes(request),
                "actual": timezone.now()
            }
        )

    def _register_class(self, request):
        form = ClassRegistrationForm(request.POST)

        try:
            class_obj = models.Class.objects.get(id=form.data["class_id"])
            course = RegistrationToCourse.objects.get(
                user=request.user,
                course_id=form.data["course_id"],
                accepted=True
            )
        except ObjectDoesNotExist:
            return self.get(request)

        if (registration := class_obj.registration) and registration.opens < timezone.now() < registration.closes:
            registered = models.RegistrationToClass.objects.filter(accepted=True, class_id=class_obj).all()
            if len(registered) < registration.capacity:
                reg = models.RegistrationToClass(
                    class_id=class_obj,
                    user=request.user
                )

                if registration.auto_approve:
                    reg.accepted = True
                    msg = "Registered :)"
                else:
                    reg.accepted = False
                    msg = "Registered but your registration needs to be approved by guarantor"

                try:
                    reg.save()
                except IntegrityError:
                    msg = "You are already registered"
                    del reg
            else:
                msg = "There is no remaining capacity in this class"
        else:
            msg = "Registration is not allowed yet"

        return render(
            request,
            "class/registration_status.html",
            {
                "class_obj": class_obj,
                "subject": course,
                "msg": msg
            }
        )

    def post(self, request):
        if "form" in request.POST:
            match request.POST["form"]:
                case "class_register":
                    return self._register_class(request)

        return self.get(request)


class ClassDetailView(GroupRequiredMixin, View):
    template_name = "class/class_detail.html"

    group_required = [u"Student"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_classes(self, request, class_id):
        try:
            class_obj = models.Class.objects.get(id=class_id)
        except ObjectDoesNotExist:
            class_obj = []

        class_dates = models.ClassDates.objects.filter(class_id=class_id)

        return {"class_obj": class_obj, "class_dates": class_dates.all()}

    def get(self, request, class_id, *args, **kwargs):
        return render(
            request, self.template_name, self._get_classes(request, class_id)
        )

