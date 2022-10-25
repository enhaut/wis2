from django.urls import path
from . import admin as a


urlpatterns = [
    path('admin/course', a.CourseAdminView.as_view(), name="course_admin"),
    path('admin/course/create', a.CreateCourseView.as_view(), name="create_course"),
    path("admin/course/<slug:id>/approve", a.ApproveCourseView.as_view(), name="approve_course"),
    path('admin/course/<slug:id>', a.EditCourseView.as_view(), name="edit_course")
]
