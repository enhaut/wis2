from django.shortcuts import render

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin


class OverviewView(LoginRequiredMixin, View):
    template_name = "overview.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

