from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
import sys
sys.path.append('..')
from login.models import User


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
        user = request.user
        if request.user.is_authenticated:
            username = user.username
            last_login = user.last_login
            email = user.email
            first_name = user.first_name
            last_name = user.last_name
            return render(request, 'student.html', {'username' : username, 'last_login' : last_login, 'email' : email, 'first_name' : first_name, 'last_name' : last_name})
        else:
            return render(request, self.template_name)


class EmployeeView(GroupRequiredMixin, View):
    template_name = "employee.html"

    group_required = [u"Teacher", u"Guarantor"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
