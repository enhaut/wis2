from django.shortcuts import render

from django.views.generic import View


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')  # TODO: enable csrf
class LoginView(View):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        return render(request, "logged.html")
