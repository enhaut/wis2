from django.urls import path
from . import admin as a


urlpatterns = [
    path('course/admin/', a.CourseAdminView.as_view(), name="course_admin")
]
