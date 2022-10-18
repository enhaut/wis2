from django.shortcuts import render
from django.views.generic import View
from braces.views import GroupRequiredMixin


class AdminView(GroupRequiredMixin, View):
    template_name = "admin.html"

    group_required = u"Administrator"
    redirect_unauthenticated_users = False
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

