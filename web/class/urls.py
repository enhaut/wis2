from django.urls import path
from . import admin


urlpatterns = [
    path('admin/class', admin.CoursesView.as_view(), name="admin_classes"),
]
