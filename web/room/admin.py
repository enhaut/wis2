from django.shortcuts import render
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.views.generic import View
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template import loader

import sys
sys.path.append('..')
import importlib
Class = importlib.import_module("class.models", "Class")
from . import models


class AdminRoomView(GroupRequiredMixin, View):
    template_name = "room_admin.html"

    group_required = u"Administrator"
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_rooms(self, request):
        rooms = {}
        try:
            rooms = models.Room.objects.all()
        except ObjectDoesNotExist:
            rooms = []

        return {"rooms": rooms}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self._get_rooms(request))


class CreateRoomForm(ModelForm):
    class Meta:
        model = models.Room
        fields = ["shortcut", "name", "capacity"]


class RemoveRoomView(GroupRequiredMixin, View):
    template_name = "rooms.html"

    group_required = [u"Administrator"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_rooms(self, id):
        try:
            return models.Room.objects.filter(
                shortcut=id
            )[0]
        except (ObjectDoesNotExist, KeyError, IndexError):
            return []

    def get(self, request, id, add_room=CreateRoomForm(), delete_room=None, *args, **kwargs):
        if not (room := self._get_rooms(id)):
            return HttpResponseNotFound(f"Room {id} could not be found!")

        if not delete_room:
            room.delete()
            return HttpResponseRedirect("/admin/rooms/")


class CreateRoomView(GroupRequiredMixin, View):
    template_name = "room_add.html"

    group_required = [u"Administrator"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"CreateForm": CreateRoomForm()})

    def post(self, request):
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)

            room.enter_by = request.user
            room.save()  # Now you can send it to DB

            return HttpResponseRedirect("/admin/rooms/")

        return render(request, self.template_name, {"CreateForm": form})


class EditRoomForm(ModelForm):
    class Meta:
        model = models.Room
        fields = ["shortcut", "name", "capacity"]


class EditRoomView(GroupRequiredMixin, View):
    template_name = "room_edit.html"

    group_required = [u"Administrator"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_rooms(self, id):
        try:
            return models.Room.objects.filter(
                shortcut=id
            )[0]
        except (ObjectDoesNotExist, KeyError, IndexError):
            return []

    def get(self, request, id, add_room=CreateRoomForm(), edit_room=None, *args, **kwargs):
        if not (room := self._get_rooms(id)):
            return HttpResponseNotFound(f"Room {id} could not be found!")

        if not edit_room:
            edit_room = EditRoomForm(
                initial={
                    "shortcut": room.shortcut,
                    "name": room.name,
                    "capacity": room.capacity
                }
            )

        return render(
            request,
            self.template_name,
            {
                "room": room,
                "form": add_room,
                "EditRoomForm": edit_room
            }
        )

    def _process_add_room_form(self, request, id):
        form = CreateRoomForm(request.POST)
        try:
            room = models.Room.objects.filter(
                Q(shortcut=id)
            )
            form = EditRoomForm(request.POST, instance=room[0])
        except ObjectDoesNotExist:
            room = None

        if form.is_valid() and room:
            form.save()
            form = CreateRoomForm()
            return redirect('room_admin')

        return self.get(request, id, edit_room=form)

    def post(self, request, id, *args, **kwargs):
        if "form" in request.POST:
            match request.POST["form"]:
                case "edit_room":
                    return self._process_add_room_form(request, id)

        return self.get(request, id)
