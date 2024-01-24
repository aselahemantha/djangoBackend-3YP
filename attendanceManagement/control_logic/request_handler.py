from datetime import datetime
from attendanceManagement.models import Employee, Attendance_Details, Device, Topic, Pin_Data
from attendanceManagement.mqtt import publish_msg


def mark_attendance(emp_id, present=True, in_time=None):
    try:
        # Get the Employee instance
        employee = Employee.objects.get(emp_id=emp_id)

        # Get the current date
        current_date = datetime.now().date()

        # Check if an entry already exists for the given employee and date
        existing_entry = Attendance_Details.objects.filter(
            emp_id=employee,
            date=current_date
        ).first()

        if existing_entry:
            # If entry exists, return it
            return existing_entry
        else:
            # If entry doesn't exist, create a new one
            attendance = Attendance_Details.objects.create(
                emp_id=employee,
                date=current_date,
                present=present,
                in_time=in_time if present else None
            )
            return attendance

    except Employee.DoesNotExist:
        print(f"Employee with emp_id={emp_id} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred while marking attendance: {str(e)}")
        return None


def get_attendance_details(emp_id, month):
    try:
        # Get the Employee instance
        employee = Employee.objects.get(emp_id=emp_id)

        # Filter attendance details based on employee and month
        attendance_details = Attendance_Details.objects.filter(
            emp_id=employee,
            date__month=month
        )

        return attendance_details

    except Employee.DoesNotExist:
        print(f"Employee with emp_id={emp_id} does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred while getting attendance details: {str(e)}")
        return []


def get_all_topic_details():
    try:
        # Filter all topic details
        topic_details = Topic.objects.all()

        return topic_details
    except Exception as e:
        print(f"An error occurred while getting topic details: {str(e)}")
        return []


def get_all_devices():
    try:
        # Filter all device details
        all_devices = Device.objects.all()

        return all_devices
    except Exception as e:
        print(f"An error occurred while getting device details: {str(e)}")
        return []


def check_pin(emp_id, pin_code):
    try:
        # Get the PIN Data instance
        pin_data = Pin_Data.objects.get(emp_id=emp_id)

        # Check if the entered pin_code matches the stored pin_code
        if pin_data.pin_code == pin_code:
            return True
        else:
            return False

    except Pin_Data.DoesNotExist:
        # Handle the case where the employee with the given emp_id is not found
        return "Pin Data not found"


def store_pin(emp_id, pin_code):
    try:
        # Create a new PIN Data instance
        pin = Pin_Data.objects.create(
            emp_id=emp_id,
            pin_code=pin_code
        )

        return "Pin stored successfully"

    except Exception as e:
        # Handle exceptions, such as IntegrityError if the emp_id already exists
        return f"Error storing pin: {str(e)}"


