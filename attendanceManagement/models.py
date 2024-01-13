import os

from django.db import models


class Employee(models.Model):
    emp_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='M')
    age = models.IntegerField()
    contact_address = models.CharField(max_length=200)
    emp_email = models.EmailField(null=False)
    emp_password = models.CharField(max_length=200, null=False)

    def __str__(self):
        return str(self.emp_id) + self.first_name + self.last_name


class Attendance_Details(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField()
    in_time = models.TimeField(null=True)

    def __str__(self):
        return str(self.attendance_id)


class Security_Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    fp_status = models.CharField(max_length=100)
    pin_status = models.CharField(max_length=100)
    lock_status = models.CharField(max_length=100)


class Pin_Data(models.Model):
    pin_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    pin_code = models.IntegerField(null=True)


def upload_fp_to(instance, filename):
    emp_id_folder = str(instance.emp_id.emp_id)
    count = Face_Data.objects.filter(emp_id=instance.emp_id).count() + 1
    filename = f"{count}.jpg"
    return os.path.join('fp_data', emp_id_folder, filename)


class Fingerprint_Data(models.Model):
    pin_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    fp = models.ImageField(upload_to=upload_fp_to, null=True, blank=True)


def upload_faces_to(instance, filename):
    emp_id_folder = str(instance.emp_id.emp_id)
    count = Face_Data.objects.filter(emp_id=instance.emp_id).count() + 1
    filename = f"{count:03d}.jpg"
    return os.path.join('datasets', emp_id_folder, filename)


class Face_Data(models.Model):
    pin_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    face = models.ImageField(upload_to=upload_faces_to, null=True, blank=True)
