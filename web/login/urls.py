from django.urls import path
from . import views, admin


urlpatterns = [
    path('', views.LoginPageView.as_view(), name="loginpage"),
    path('do_login', views.LoginView.as_view(), name="login"),
    path('logout', views.LogoutView.as_view(), name="logout"),
    path('courses', views.AvailableCoursesView.as_view(), name="non_registered"),
    path('course/<slug:shortcut>', views.CourseContentView.as_view(), name="course_content"),
    path('edit_profile', views.EditProfileView.as_view(), name="edit_profile"),
    path("admin/user_management", views.UserManagementView.as_view(), name="user_management")
]
