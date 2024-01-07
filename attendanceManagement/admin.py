from django.contrib import admin
from .models import Employee, Attendance_Details, Job_Title, Department, Duty_Duration, Topic

# Register your models here.

admin.site.register(Employee)
admin.site.register(Attendance_Details)
admin.site.register(Job_Title)
admin.site.register(Department)
admin.site.register(Duty_Duration)
admin.site.register(Topic)