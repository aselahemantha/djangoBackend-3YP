import datetime
from attendanceManagement.models import Employee, Attendance_Details


def process_attendance_data(data):
    emp_id = data.get('id')
    cmd = data.get('cmd')

    try:
        employee = Employee.objects.get(emp_id=emp_id)
        today = datetime.date.today()

        # Check if attendance for today already exists
        existing_attendance = Attendance_Details.objects.filter(emp_id=employee, date=today).exists()

        if cmd == 'marked' and not existing_attendance:
            Attendance_Details.objects.create(
                emp_id=employee,
                date=today,
                present=True,
                in_time=datetime.datetime.now().time(),
            )
            return f"Attendance for Employee with ID {emp_id} is marked successfully"
        elif existing_attendance:
            return f"Attendance for Employee with ID {emp_id} already marked for today."
    except Employee.DoesNotExist:
        return f"Employee with ID {emp_id} not found."
