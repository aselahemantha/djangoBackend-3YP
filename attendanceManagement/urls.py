from django.urls import path
from . import views

# URL Configuration
urlpatterns = [
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('configure/', views.ConfigureDeviceView.as_view(), name='configure'),
    path('active/', views.ActiveDeviceView.as_view(), name='active'),
    path('mark-attendance/', views.MarkAttendanceView.as_view(), name='attendance'),
    path('store-faces/', views.StoreFacesView.as_view(), name='faces'),
    path('encode-faces/', views.EncodeFaces.as_view(), name='encode-faces'),
    path('store-fp/', views.StoreFPView.as_view(), name='fp'),  # Not Used
    path('get-attendance/<int:emp_id>/<int:month>/', views.GetAttendanceView.as_view(), name='get-attendance'),
    path('get-all-topic/', views.GetAllTopicView.as_view(), name='get-all-topic'),
    path('get-all-device', views.GetAllDeviceView.as_view(), name='get-all-devices'),
    path('check-pin/', views.CheckPinView.as_view(), name='check-pin'),
    path('save-pin/', views.StorePinView.as_view(), name='store-pin'),
    path('save-device-lock/', views.StoreDeviceLockView.as_view(), name='store-lock'),
    path('save-topic/', views.SaveTopicView.as_view(), name='save-topic'),
    path('save-device/', views.SaveDeviceView.as_view(), name='save-device'),
    path('save-department/', views.SaveDepartmentView.as_view(), name='save-department'),
    path('create_employee/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('get-emp/<emp_email>/', views.GetEmployeeDetailsView.as_view(), name='get-emp'),
]
