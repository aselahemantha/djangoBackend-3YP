from django.contrib import admin
from .models import Employee, Attendance_Details, Face_Data

# Register your models here.

admin.site.register(Employee)
admin.site.register(Attendance_Details)
admin.site.register(Face_Data)