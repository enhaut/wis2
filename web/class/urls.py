from django.urls import path
from . import admin


urlpatterns = [
    path('admin/class', admin.CoursesView.as_view(), name="admin_classes"),
    path('admin/class/<slug:id>', admin.ClassView.as_view(), name="view_classes"),
    path('admin/class/<slug:id>/<int:class_id>', admin.EditClassView.as_view(), name="edit_class"),
    path('admin/class/<slug:id>/<int:class_id>/<int:date_id>/remove', admin.RemoveClassDatesView.as_view(), name="remove_date"),
    path('admin/class/<slug:id>/<int:class_id>/registrations', admin.RegistrationSettingsView.as_view(), name="class_reg"),
]
