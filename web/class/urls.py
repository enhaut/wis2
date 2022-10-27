from django.urls import path
from . import admin


urlpatterns = [
    path('admin/class', admin.CoursesView.as_view(), name="admin_classes"),
    path('admin/class/<slug:id>', admin.ClassView.as_view(), name="view_classes"),
]
