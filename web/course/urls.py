from django.urls import path
from . import admin as a
from . import views


urlpatterns = [
    path('courses/registration', views.RegistrationOverviewView.as_view(), name="course_registrations_overview"),
    path('courses/registration/<slug:subject>', views.RegistrationView.as_view(), name="course_registrations"),

    path('admin/course', a.CourseAdminView.as_view(), name="course_admin"),
    path('admin/course/create', a.CreateCourseView.as_view(), name="create_course"),
    path("admin/course/<slug:id>/approve", a.ApproveCourseView.as_view(), name="approve_course"),
    path('admin/course/<slug:id>/registrations', a.RegistrationSettingsView.as_view(), name="registrations"),
    path('admin/course/<slug:id>', a.EditCourseView.as_view(), name="edit_course"),
    path('admin/course/<slug:id>/approve_registration/<slug:user>', a.ApproveRegistrationView.as_view(), name="appr_course_reg")
]
