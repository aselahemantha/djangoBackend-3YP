from django.contrib import admin
from .models import Employee, Attendance_Details, Face_Data, Fingerprint_Data, Topic, Pin_Data, Device, Department

# Register your models here.

admin.site.register(Employee)
admin.site.register(Attendance_Details)
admin.site.register(Face_Data)
admin.site.register(Device)
admin.site.register(Department)
admin.site.register(Topic)
admin.site.register(Pin_Data)
admin.site.register(Fingerprint_Data)