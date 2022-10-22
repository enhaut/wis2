from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin


class OverviewView(LoginRequiredMixin, View):
    template_name = "overview.html"

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Student').exists():
            return HttpResponseRedirect('/student')
        elif request.user.groups.filter(name="Teacher").exists():
            return HttpResponseRedirect('/employee')
        elif request.user.groups.filter(name="Guarantor").exists():
            return HttpResponseRedirect('/employee')
        elif request.user.groups.filter(name="Administrator").exists():
            return HttpResponseRedirect('/employee')
        else:
            return HttpResponseRedirect('/overview')


class StudentView(GroupRequiredMixin, View):
    template_name = "student.html"

    group_required = u"Student"
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class EmployeeView(GroupRequiredMixin, View):
    template_name = "employee.html"

    group_required = [u"Teacher", u"Guarantor"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
