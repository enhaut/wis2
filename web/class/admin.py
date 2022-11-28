from django import forms
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone


from datetime import datetime, timedelta
import sys
from . import models
sys.path.append('..')
from course.models import Course
from course.models import RegistrationToCourse
from room.models import Room
from course.admin import RegistrationSettingsViewBase
from django.forms import ModelForm

from . import models

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

        return courses.distinct()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"courses": self._get_courses(request)})


class CreateClassForm(forms.ModelForm):
    class Meta:
        model = models.Class
        fields = ["type", "name", "description"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "placeholder": "HTML input is supported"
                }
            )
        }


def validate_class_exists(id):
    try:
        models.Class.objects.get(pk=id)
    except ObjectDoesNotExist:
        raise ValidationError(
            _(f'{id} does not exist')
        )


class RemoveClassForm(forms.Form):
    id = forms.IntegerField(
        label='id',
        validators=[
            validate_class_exists,
        ]
    )


class ClassView(GroupRequiredMixin, View):
    template_name = "class/admin/classes.html"

    group_required = [u"Guarantor", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_classes(self, request, id):
        try:
            classes = models.Class.objects.filter(
                course=id
            )
        except ObjectDoesNotExist:
            return []

        return classes

    def get(self, request, id, create_form=None, *args, **kwargs):
        try:
            courses = Course.objects.filter(
                Q(shortcut=id, lectors=request.user) | Q(shortcut=id, guarantor=request.user)
            )
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        if not courses:
            return HttpResponse(status=404)

        if not create_form:
            create_form = CreateClassForm()

        return render(
            request,
            self.template_name,
            {
                "classes": self._get_classes(request, id),
                "CreateClassForm": create_form,
                "now": datetime.now()
            }
        )

    def _is_authorized(self, request, id):
        if not (course := Course.objects.filter(
                Q(shortcut=id, lectors=request.user) | Q(shortcut=id, guarantor=request.user)
            )):
            return False
        return course

    def _process_create_class_form(self, request, id):
        form = CreateClassForm(request.POST)
        if not (course := self._is_authorized(request, id)):
            return HttpResponse(status=400)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = course

            obj.save()
            form = CreateClassForm()

        return self.get(request, id, create_form=form)

    def _process_remove_class_form(self, request, id):
        if not (course := self._is_authorized(request, id)):
            return HttpResponse(status=400)

        form = RemoveClassForm(request.POST)
        if form.is_valid():
            obj = models.Class.objects.get(pk=form.data["id"])
            obj.delete()

        return self.get(request, id)

    def post(self, request, id):
        if "form" in request.POST:
            match request.POST["form"]:
                case "create_class":
                    return self._process_create_class_form(request, id)
                case "remove_class":
                    return self._process_remove_class_form(request, id)

        return self.get(request, id)


class AcceptStudentForm(forms.Form):
    student = forms.CharField(
        max_length=8
    )


class AddClassDateForm(forms.ModelForm):
    class Meta:
        model = models.ClassDates
        fields = ["date_from", "date_to"]
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
            )
        }


class EditRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["shortcut"]


class EditClassView(GroupRequiredMixin, View):
    template_name = "class/admin/class.html"

    group_required = [u"Guarantor", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_class(self, request, course, class_id):
        try:
            return models.Class.objects.filter(
                Q(
                    course=course,
                    course__lectors=request.user,
                    pk=class_id
                ) | Q(
                    course=course,
                    course__guarantor=request.user,
                    pk=class_id
                )
            )[0]
        except (ObjectDoesNotExist, IndexError):
            raise

    def _get_edit_form(self, request, class_obj):
        edit_form = CreateClassForm(
            initial={
                "type": class_obj.type,
                "name": class_obj.name,
                "description": class_obj.description,
            }
        )
        if not request.user.groups.filter(name="Guarantor").exists():
            edit_form.fields["type"].disabled = True
            edit_form.fields["name"].disabled = True
            edit_form.fields["description"].disabled = True

        return edit_form

    def _get_students_points(self, class_obj):
        points = {}
        for student in class_obj.students.all():
            points[student.username] = 0
            try:
                assessments = models.Assessment.objects.filter(student=student, evaluated_class=class_obj)
            except ObjectDoesNotExist:
                points[student.username] = None

            points[student.username] = sum(assessment.point_evaluation for assessment in assessments)

        return points

    def _get_class_dates(self, class_obj):
        return models.ClassDates.objects.filter(
            class_id=class_obj
        ).all()

    def _get_rooms(self, class_obj):
        return class_obj.rooms.all(), Room.objects.all()

    def get(self, request, id, class_id, edit_form = None, add_class_form = None, add_room_form = None, *args, **kwargs):
        try:
            class_obj = self._get_class(request, id, class_id)
        except (ObjectDoesNotExist, IndexError):
            return HttpResponse(status=404)

        if not edit_form:
            edit_form = self._get_edit_form(request, class_obj)

        if not add_class_form:
            add_class_form = AddClassDateForm()

        if not edit_form:
            add_room_form = EditRoomForm()

        class_rooms, avail_rooms = self._get_rooms(class_obj)

        registered = {}
        for regs in models.RegistrationToClass.objects.filter(class_id=class_obj):
            registered[regs.user.username] = regs.accepted

        return render(
            request,
            self.template_name,
            {
                "class": class_obj,
                "CreateClassForm": edit_form,
                "students": class_obj.students.select_related(),
                "registered": registered,
                "points": self._get_students_points(class_obj),
                "classes": self._get_class_dates(class_obj),
                "CreateClassDateForm": add_class_form,
                "EditRoomForm": add_room_form,
                "rooms": class_rooms,
                "avail_rooms": avail_rooms
            }
        )

    def _process_edit_class_form(self, request, course, class_id):
        form = CreateClassForm(request.POST)

        if (not (class_obj := self._get_class(request, course, class_id))):
            return HttpResponse(status=400)
        if form.is_valid():
            try:
                class_type = models.TypeOfClass.objects.get(pk=form.data["type"])
            except ObjectDoesNotExist:
                return HttpResponse(status=400)

            class_obj.type = class_type
            class_obj.name = form.data["name"]
            class_obj.description = form.data["description"]

            try:
                class_obj.save()
            except ValidationError:
                form.add_error("closes", "Invalid data format")

        return self.get(request, course, class_id, form if not form.errors else None)

    def _accept_student(self, request, course, class_id):
        if (not (class_obj := self._get_class(request, course, class_id))):
            return HttpResponse(status=403)

        form = RemoveClassForm(request.POST)

        try:
            registration = models.RegistrationToClass.objects.get(
                class_id=class_id,
                user=form.data["student"],
                accepted=0
            )
            registration.accepted = 1
            registration.save()
        except (ObjectDoesNotExist, ValidationError):
            pass
        return self.get(request, course, class_id, None)

    def _add_class_date(self, request, id, class_id):
        if (not (class_obj := self._get_class(request, id, class_id))):
            return HttpResponse(status=400)

        form = AddClassDateForm(request.POST)

        try:
            class_obj = models.Class.objects.get(id=class_id)
        except ObjectDoesNotExist:
            return self.get(request, id, class_id, add_class_form=form)

        if form.data["date_to"] < form.data["date_from"]:
            form.add_error("date_to", "Date to needs to be bigger than date from")
            return self.get(request, id, class_id, add_class_form=form)

        date_from = make_aware(
            datetime.strptime(form.data["date_from"], "%Y-%m-%dT%H:%M"),
            get_current_timezone(),
            False
        )
        date_to = make_aware(
            datetime.strptime(form.data["date_to"], "%Y-%m-%dT%H:%M"),
            get_current_timezone(),
            False
        )

        class_date = models.ClassDates(
            class_id=class_obj,
            date_from=date_from,
            date_to=date_to
        )
        class_date.save()

        return self.get(request, id, class_id, add_class_form=None)

    def _add_room(self, req, id, class_id):
        if (not (class_obj := self._get_class(req, id, class_id))):
            return HttpResponse(status=400)

        form = EditRoomForm(req.POST)

        try:
            room = Room.objects.get(shortcut=form.data["shortcut"])
            class_obj = models.Class.objects.get(id=class_id)
        except ObjectDoesNotExist:
            form.add_error("shortcut", "Invalid room!")
            return self.get(req, id, class_id, add_room_form=form)

        if models.Class.objects.filter(id=class_id, rooms=room).exists():
            form.add_error("shortcut", "Room is already assigned to this course!")
            return self.get(req, id, class_id, add_room_form=form)

        class_obj.rooms.add(room)
        class_obj.save()

        return self.get(req, id, class_id, add_room_form=None)

    def _remove_room(self, req, id, class_id):
        if (not (class_obj := self._get_class(req, id, class_id))):
            return HttpResponse(status=400)

        form = EditRoomForm(req.POST)

        try:
            room = Room.objects.get(shortcut=form.data["shortcut"])
            class_obj = models.Class.objects.get(id=class_id)
        except ObjectDoesNotExist:
            form.add_error("shortcut", "Invalid room!")
            return self.get(req, id, class_id, add_room_form=form)

        if not models.Class.objects.filter(rooms=room).exists():
            form.add_error("shortcut", "Room does not exists!")
            return self.get(req, id, class_id, add_room_form=form)

        class_obj.rooms.remove(room)
        class_obj.save()

        return self.get(req, id, class_id, add_room_form=None)

    def post(self, request, id, class_id):
        if "form" in request.POST:
            match request.POST["form"]:
                case "edit_class":
                    return self._process_edit_class_form(request, id, class_id)
                case "accept_student":
                    return self._accept_student(request, id, class_id)
                case "add_class_date":
                    return self._add_class_date(request, id, class_id)
                case "add_room":
                    return self._add_room(request, id, class_id)
                case "remove_room":
                    return self._remove_room(request, id, class_id)

        return self.get(request, id, class_id)


class RegistrationForm(forms.ModelForm):
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


class RegistrationSettingsView(RegistrationSettingsViewBase):
    template_name = "class/admin/registrations.html"

    def _get_class(self, request, course, class_id):
        try:
            return models.Class.objects.filter(
                    Q(
                        course=course,
                        course__lectors=request.user,
                        pk=class_id
                    ) | Q(
                        course=course,
                        course__guarantor=request.user,
                        pk=class_id
                    )
                )[0]
        except (ObjectDoesNotExist, IndexError):
            return None

    def get(self, request, id, class_id, form=None, *args, **kwargs):
        if not (class_obj := self._get_class(request, id, class_id)):
            return HttpResponseNotFound(f"Class {id} could not be found!")

        if form is None:
            form = RegistrationForm(
                initial=self._get_form_values(class_obj)
            )

        return render(
            request,
            self.template_name,
            {
                "RegistrationForm": form,
                "class": class_obj
            }
        )

    def post(self, request, id, class_id):
        form = RegistrationForm(request.POST)

        if not (class_obj := self._get_class(request, id, class_id)):
            return HttpResponseNotFound(f"Course {id} could not be found!")

        form = self._process_registration_form(form, class_obj)

        return self.get(request, id, class_id, form)

class AddPointsForm(forms.Form):
    points = forms.FloatField(label='points', widget=forms.NumberInput(attrs={"min" : 0, "max" : 101}))

class RemovePointsForm(forms.Form):
    assessment_id = forms.IntegerField(label='assessment_id')

class EvaluateStudentView(GroupRequiredMixin, View):
        template_name = "evaluate_student.html"

        group_required = [u"Guarantor", u"Teacher"]
        redirect_unauthenticated_users = False
        raise_exception = True

        def _get_classes(self, request, shortcut, student_name, *args, **kwargs):
            classes = []

            course = RegistrationToCourse.objects.get(accepted=True, user=student_name, course_id=shortcut)

            course_classes = models.Class.objects.filter(course=course.course_id)
            registrations = models.RegistrationToClass.objects.filter(class_id__in=course_classes, user=student_name, accepted=True)
            for registration in registrations:
                classes.append(registration.class_id)
            return classes

        def _process_add_points_form(self, request, id, student_name):
            form = AddPointsForm(request.POST)
            try:
                course = models.Course.objects.filter(
                    Q(shortcut=id, lectors=request.user) | Q(shortcut=id, guarantor=request.user))
                my_evaluated_class = models.Class.objects.get(id=form.data["class_id"])
                student_name = models.User.objects.get(username=student_name)
            except ObjectDoesNotExist:
                form.add_error("description", "You are not a teacher/guarantor of this course")
                course = None
                return HttpResponseNotFound(f"Class {id} could not be found!")
            if form.is_valid() and course:
                assessment = models.Assessment()
                assessment.point_evaluation = float(form.data['points'])
                assessment.published_date = timezone.now()
                assessment.evaluated_class = my_evaluated_class
                assessment.entered_points_by = request.user
                assessment.student = student_name
                assessment.save()
            else:
                return HttpResponseNotFound(f"You are not a teacher/guarantor of this course so you can't change points!")

            return self.get(request, id, student_name)

        def _process_remove_points_form(self, request, id, student_name):
            form = RemovePointsForm(request.POST)
            try:
                course = models.Course.objects.filter(
                    Q(shortcut=id, lectors=request.user) | Q(shortcut=id, guarantor=request.user))
                student_name = models.User.objects.get(username=student_name)
                assessment = models.Assessment.objects.get(id=form.data["assessment_id"], evaluated_class=form.data["class_id"], student=student_name)
            except ObjectDoesNotExist:
                form.add_error("description", "You are not a teacher/guarantor of this course")
                course = None
                return HttpResponseNotFound(f"Class {id} could not be found!")
            if form.is_valid() and course:
                assessment.delete()
            else:
                return HttpResponseNotFound(f"You are not a teacher/guarantor of this course so you can't change points!")

            return self.get(request, id, student_name)

        def post(self, request, id, student_name):
            if "form" in request.POST:
                match request.POST["form"]:
                    case "add_points":
                        return self._process_add_points_form(request, id, student_name)
                    case "remove_points":
                        return self._process_remove_points_form(request, id, student_name)
            return self.get(request, id, student_name)
        def get(self, request, id, student_name, add_points=AddPointsForm(), *args, **kwargs):
            if request.user.is_authenticated:
                course = Course.objects.get(shortcut=id)
                assessments = models.Assessment.objects.filter(evaluated_class__in=self._get_classes(request, id, student_name), student=student_name)
                return render(request, "evaluate_student.html", {'course' : course, 'student_name' : student_name, 'classes' : self._get_classes(request, id, student_name), 'form' : add_points, 'assessments' : assessments})

class RemoveClassDatesView(RegistrationSettingsViewBase):
    def _remove_class_date(self, request, subject, class_id, date_id):
        try:
            date_obj = models.ClassDates.objects.get(
                Q(
                    id=date_id,
                    class_id=class_id,
                    course__class_id__course__lectors=request.user
                ) | Q(
                    id=date_id,
                    class_id=class_id,
                    course__class_id__course__guarantor=request.user,
                )
            )
        except ObjectDoesNotExist:
            return HttpResponse(status=400)

        date_obj.delete()

        return redirect("edit_class", id=subject, class_id=class_id)

    def get(self, request, id, class_id, date_id):
        return self._remove_class_date(request, id, class_id, date_id)
