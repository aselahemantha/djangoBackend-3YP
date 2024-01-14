from django.urls import path
from . import views

# URL Configuration
urlpatterns = [
    path('logout/', views.LogoutView.as_view(), name ='logout'),
    path('configure/', views.ConfigureDeviceView.as_view(), name='configure'),
    path('active/', views.ActiveDeviceView.as_view(), name='active'),
    path('mark_attendance/', views.MarkAttendanceView.as_view(), name='attendance'),
    path('store_faces/', views.StoreFacesView.as_view(), name='faces'),
    path('encode_faces/', views.EncodeFaces.as_view(), name='encode-faces'),
    path('store_fp/', views.StoreFPView.as_view(), name='fp'),
    path('get_attendance/<int:emp_id>/<int:month>/', views.GetAttendanceView.as_view(), name='get-attendance'),
]


