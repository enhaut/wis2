from django.urls import path
from . import views


urlpatterns = [
    path("overview", views.OverviewView.as_view(), name="overview"),
    path("student", views.StudentView.as_view(), name="student"),
    path("employee", views.EmployeeView.as_view(), name="employee")
]
