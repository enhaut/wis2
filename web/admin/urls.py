from django.urls import path
from . import views


urlpatterns = [
    path("admin/", views.AdminView.as_view())
]
