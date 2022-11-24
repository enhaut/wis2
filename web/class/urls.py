from django.urls import path
from . import admin, views


urlpatterns = [
    path('admin/class', admin.CoursesView.as_view(), name="admin_classes"),
    path('admin/class/<slug:id>', admin.ClassView.as_view(), name="view_classes"),
    path('admin/class/<slug:id>/<int:class_id>', admin.EditClassView.as_view(), name="edit_class"),
    path('admin/class/<slug:id>/<int:class_id>/registrations', admin.RegistrationSettingsView.as_view(), name="class_reg"),
    path('admin/class/<slug:id>/<slug:student_name>/evaluation', admin.EvaluateStudentView.as_view(), name="evaluate_student")
]
