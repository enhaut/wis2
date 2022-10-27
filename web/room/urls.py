from django.urls import path
from . import admin as a


urlpatterns = [
    path('admin/rooms/', a.AdminRoomView.as_view(), name="room_admin"),
    path('admin/rooms/create', a.CreateRoomView.as_view(), name="room_add"),
    path('admin/rooms/<slug:id>', a.EditRoomView.as_view(), name="room_edit"),
    path('admin/rooms/<slug:id>/delete', a.RemoveRoomView.as_view(), name="room_delete"),
]
