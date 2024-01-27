from django.contrib import admin
from .models import Employee, Attendance_Details, Topic, Pin_Data, Device, Department

# Register your models here.

admin.site.register(Employee)
admin.site.register(Attendance_Details)
admin.site.register(Device)
admin.site.register(Department)
admin.site.register(Topic)
admin.site.register(Pin_Data)
