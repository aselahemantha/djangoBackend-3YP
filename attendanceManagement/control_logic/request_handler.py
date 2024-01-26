from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile

from attendanceManagement.models import Employee, Attendance_Details, Device, Topic, Pin_Data, Face_Data, Department
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


def update_device_lock_status(device_id, lock_status):
    try:
        device = Device.objects.get(device_id=device_id)
        device.lock_status = lock_status
        device.save()
        return True
    except ObjectDoesNotExist:
        return False


def save_face_data(employee_instance, face_image):
    # Assuming you have an Employee instance with emp_id
    # Create a Face_Data instance
    image = ContentFile(face_image)
    face_data_instance = Face_Data(emp_id=employee_instance, face=image)

    face_data_instance.save()


def store_department(name, description, topic_id):
    try:
        # Get the PIN Data instance
        topic_data = Topic.objects.get(topic_id=topic_id)

        department = Department.objects.create(
            department_name=name,
            department_description=description,
            topic_id=topic_data
        )

        return "Department stored successfully"

    except Topic.DoesNotExist:
        # Handle the case where the employee with the given emp_id is not found
        return "Topic Data not found"


def store_topic(name):
    try:
        topic = Topic.objects.create(
            topic_name=name
        )

        return "Topic stored successfully"

    except Exception as e:
        return "Error storing"


def store_device(device_id, topic_id, department_id, MAC, lock_status):
    try:
        # Get the PIN Data instance
        topic_data = Topic.objects.get(topic_id=topic_id)
        department_data = Department.objects.get(department_id=department_id)

        device = Device.objects.create(
            device_id=device_id,
            topic_id=topic_data,
            department_id=department_data,
            MAC=MAC,
            lock_status=lock_status
        )

        return "Device stored successfully"

    except Topic.DoesNotExist:
        # Handle the case where the employee with the given emp_id is not found
        return "Topic Data not found"

    except Department.DoesNotExist:
        # Handle the case where the employee with the given emp_id is not found
        return "Department Data not found"


def get_all_topics():
    try:
        # Filter all device details
        all_topics = Topic.objects.all()

        return all_topics
    except Exception as e:
        print(f"An error occurred while getting device details: {str(e)}")
        return []


def get_all_departments():
    try:
        # Filter all device details
        all_departments = Department.objects.all()

        return all_departments
    except Exception as e:
        print(f"An error occurred while getting device details: {str(e)}")
        return []

def get_emp_details(emp_email):
    try:
        # Get the Employee instance
        employee = Employee.objects.get(emp_email=emp_email)

        return employee

    except Employee.DoesNotExist:
        print(f"Employee with emp_email={emp_email} does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred while getting attendance details: {str(e)}")
        return []
