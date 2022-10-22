from django.urls import path
from . import admin as a


urlpatterns = [
    path('admin/course', a.CourseAdminView.as_view(), name="course_admin"),
    path('admin/course/<slug:id>', a.EditCourseView.as_view(), name="edit_course")
]
