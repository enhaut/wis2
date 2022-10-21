from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin


class OverviewView(LoginRequiredMixin, View):
    template_name = "overview.html"

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Student').exists():
            return HttpResponseRedirect('/student')
        else:
            return HttpResponseRedirect('/employee')

class StudentView(LoginRequiredMixin, View):
    template_name = "student.html"

    #group_required = u"Administrator"
    #redirect_unauthenticated_users = False
    #raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class EmployeeView(LoginRequiredMixin, View):
    template_name = "employee.html"

    #group_required = u"Administrator"
    #redirect_unauthenticated_users = False
    #raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)