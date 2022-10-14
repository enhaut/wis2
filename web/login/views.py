from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import logout

from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from . import basic_auth as auth


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
