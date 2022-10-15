from django.urls import path
from . import views


urlpatterns = [
    path('', views.LoginPageView.as_view(), name="loginpage"),
    path('do_login', views.LoginView.as_view(), name="login"),
    path('logout', views.LogoutView.as_view())
]
