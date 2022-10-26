from django.db.models import Q
from django.shortcuts import render
from django.views.generic import View
from braces.views import GroupRequiredMixin

import sys
sys.path.append('..')
from course.models import Course


class CoursesView(GroupRequiredMixin, View):
    template_name = "class/admin/courses.html"

    group_required = [u"Guarantor", u"Teacher"]
    redirect_unauthenticated_users = False
    raise_exception = True

    def _get_courses(self, request):
        courses = Course.objects.filter(
            Q(lectors=request.user) | Q(guarantor=request.user)
        )
        return courses

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"courses": self._get_courses(request)})
