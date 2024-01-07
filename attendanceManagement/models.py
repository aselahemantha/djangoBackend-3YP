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


class Topic(models.Model):
    topic_id = models.AutoField(primary_key=True)
    topic_name = models.CharField(max_length=50)
    dev_connected = models.IntegerField()

    def __str__(self):
        return str(self.topic_id) + self.topic_name


class Department(models.Model):
    dep_id = models.AutoField(primary_key=True)
    dep_name = models.CharField(max_length=100)
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE)
    no_emp = models.IntegerField()

    def __str__(self):
        return str(self.dep_id) + self.dep_name


class Attendance_Details(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField()
    in_time = models.TimeField()
    out_time = models.TimeField()

    def __str__(self):
        return str(self.attendance_id)


class Job_Title(models.Model):
    job_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    dep_id = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.job_id) + self.title


class Duty_Duration(models.Model):
    duty_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    job_id = models.ForeignKey(Job_Title, on_delete=models.CASCADE)
    duration = models.IntegerField()

    def __str__(self):
        return str(self.duty_id)