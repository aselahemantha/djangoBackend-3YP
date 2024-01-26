import os
import base64

from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from attendanceManagement.models import Face_Data, Employee, Fingerprint_Data, Department
from attendanceManagement.mqtt import publish_msg
from attendanceManagement.control_logic import request_handler
from django.conf import settings
from attendanceManagement.face_detection import recognize_faces_image, encode_faces
from attendanceManagement.control_logic import request_handler

'''
Home -> Home Page
Log Out -> Log Out Function
Configure Device -> Configure Device Function
Active Device -> Active Device Function
Mark Attendance -> Mark Attendance Function
Store Faces -> Store Faces of the Employees
GetAttendanceView
'''

class HomeView(APIView):
    #permission_classes = (IsAuthenticated,)

    def get(self, request):
        return render(request, 'index.html')


# Log Out REST endpoint
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Configure Mode REST endpoint
class ConfigureDeviceView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            publish_msg.run(request.data)

            return Response({'message': 'Configuration sent to MQTT'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Failed to send configuration to MQTT: {e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Active Mode REST endpoint
class ActiveDeviceView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            publish_msg.run(request.data)

            return Response({'message': 'Activation sent to MQTT'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Failed to send activation to MQTT: {e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Storing the photo and mark attendance REST endpoint
class MarkAttendanceView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            print(request.data)
            image_file_64 = request.data.get('image')
            in_time = request.data.get('in_time')

            if not image_file_64:
                return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Decode the image file
            image_file = base64.b64decode(image_file_64)
            # Save the image to a folder
            image_path = self.save_image(image_file)
            print(image_path)
            emp_id = self.get_name(image_path)
            request_handler.mark_attendance(emp_id=emp_id, present=True, in_time=in_time)

            return Response({
                'message': f'Image saved successfully for Employee ID: {emp_id}',
                'image_path': image_path,
                'emp_id': emp_id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def save_image(self, image_file):
        save_path = 'captured'  # Folder name
        file_name = 'capture.jpg'  # Fixed filename

        # Full path where the image will be saved
        full_path = os.path.join(settings.MEDIA_ROOT, save_path, file_name)

        os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

        # Write the byte data directly to the file
        with open(full_path, 'wb') as destination:
            destination.write(image_file)

        return full_path

    def get_name(self, image_file):
        id_arr = recognize_faces_image.recognize_face(image_file)

        if len(id_arr) == 1:
            return id_arr[0]


class StoreFacesView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            image_file_64 = request.data.get('image')
            emp_id_value = request.data.get('emp_id')

            if not image_file_64 or not emp_id_value:
                return Response({'error': 'Image file and Employee ID are required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                emp_id = int(emp_id_value)
                employee = get_object_or_404(Employee, emp_id=emp_id)
            except ValueError:
                return Response({'error': 'Invalid emp_id format'}, status=status.HTTP_400_BAD_REQUEST)

            # Decode the image file
            image_file = base64.b64decode(image_file_64)

            # Save the image using a function similar to save_image
            image_path = self.save_face_image(image_file, employee)
            request_handler.save_face_data(employee, image_file)

            return Response({'message': 'Image saved successfully', 'image_path': image_path},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def save_face_image(self, image_file, employee):
        save_path = 'datasets'  # Folder name
        count = Face_Data.objects.filter(emp_id=employee).count() + 1
        filename = f"{count}.jpg"

        # Full path where the image will be saved
        full_path = os.path.join(settings.MEDIA_ROOT, save_path, str(employee.emp_id), filename)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path, str(employee.emp_id)), exist_ok=True)

        with open(full_path, 'wb') as destination:
            destination.write(image_file)

        return full_path


# Encode Faces REST endpoint
class EncodeFaces(APIView):
    def get(self, request, *args, **kwargs):
        try:
            message = encode_faces.quantify_faces()
            return Response({'message': message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Storing the fingerprints REST endpoint
class StoreFPView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            image_file = request.data.get('image')
            emp_id_value = request.data.get('emp_id')

            if not image_file or not emp_id_value:
                return Response({'error': 'Image file and Employee ID are required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                emp_id = int(emp_id_value)
                employee = get_object_or_404(Employee, emp_id=emp_id)
            except ValueError:
                return Response({'error': 'Invalid emp_id format'}, status=status.HTTP_400_BAD_REQUEST)

            # Save the image to the specified path using the upload_to function
            fp_data = Fingerprint_Data(emp_id=employee, face=image_file)
            fp_data.save()

            # Get the saved image path
            image_path = fp_data.fp.url

            return Response({'message': 'Fingerprint saved successfully', 'image_path': image_path},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get Attendance Details REST endpoint
class GetAttendanceView(APIView):
    def get(self, request, emp_id, month):
        try:
            emp_id = int(emp_id)
            month = int(month)

            # Call the get_attendance_details function
            attendance_details = request_handler.get_attendance_details(emp_id=emp_id, month=month)

            # Serialize the attendance details into a JSON response
            serialized_data = []
            for attendance in attendance_details:
                serialized_data.append({
                    'attendance_id': attendance.attendance_id,
                    'date': attendance.date,
                    'present': attendance.present,
                    'in_time': attendance.in_time.strftime('%H:%M') if attendance.in_time else None,
                })

            return JsonResponse({'attendance_details': serialized_data}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Invalid emp_id or month'}, status=400)


# Get All Topic Details REST endpoint
class GetAllTopicView(APIView):
    def get(self, request):
        try:
            # Call the get_attendance_details function
            topic_details = request_handler.get_all_topic_details()

            # Serialize the attendance details into a JSON response
            serialized_data = []
            for topic in topic_details:
                serialized_data.append({
                    'topic_id': topic.topic_id,
                    'topic_name': topic.topic_name,
                })

            return JsonResponse({'all_topics': serialized_data}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Invalid request'}, status=400)


# Get All Device Details REST endpoint
class GetAllDeviceView(APIView):
    def get(self, request):
        try:
            # Call the get_all_device function
            all_devices = request_handler.get_all_devices()

            # Serialize the attendance details into a JSON response
            serialized_data = []
            for device in all_devices:
                serialized_data.append({
                    'device_id': device.device_id,
                    'active': device.active,
                    'topic_id': device.topic_id,
                    'department_id': device.department_id,
                })

            return JsonResponse({'all_topics': serialized_data}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Invalid request'}, status=400)


# Check entered pin
class CheckPinView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            emp_id_value = request.data.get('emp_id')
            pin_code = request.data.get('pin_code')

            if not pin_code or not emp_id_value:
                return Response({'error': 'PIN Code and Employee ID are required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                state = request_handler.check_pin(emp_id_value, pin_code)

                return Response({'message': 'Unlock Door', 'Status': state},
                                status=status.HTTP_200_OK)

            except ValueError:
                return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Save New PIN to the database
class StorePinView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            emp_id_value = request.data.get('emp_id')
            pin_code = request.data.get('pin_code')

            if not pin_code or not emp_id_value:
                return Response({'error': 'PIN Code and Employee ID are required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                state = request_handler.store_pin(emp_id_value, pin_code)

                return Response({'message': 'Pin Code Processing: ', 'Status': state},
                                status=status.HTTP_200_OK)

            except ValueError:
                return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Save device lock statue
class StoreDeviceLockView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            device_id = request.data.get('device_id')
            lock_state = request.data.get('lock_state')

            if not device_id or not lock_state:
                return Response({'error': 'Device ID and State are required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                state = request_handler.update_device_lock_status(device_id, lock_state)

                return Response({'message': 'Pin Code Processing: ', 'Status': state},
                                status=status.HTTP_200_OK)

            except ValueError:
                return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Save new Department
class SaveDepartmentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            department_name = request.data.get('department_name')
            department_description = request.data.get('department_description')
            topic_id = request.data.get('topic_id')

            if not topic_id or not department_name:
                return Response({'error': 'Department Name and Topic ID are required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                state = request_handler.store_department(department_name, department_description, topic_id)

                return Response({'message': 'Department Processing: ', 'Status': state},
                                status=status.HTTP_200_OK)

            except ValueError:
                return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            # Call the get_all_device function
            all_departments = request_handler.get_all_departments()

            # Serialize the attendance details into a JSON response
            serialized_data = []
            for department in all_departments:

                topic_dict = model_to_dict(department.topic_id)

                serialized_data.append({
                    'department_id': department.department_id,
                    'department_name': department.department_name,
                    'department_description': department.department_description,
                    'topic_data': topic_dict,
                })

            return JsonResponse({'all_departments': serialized_data}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Invalid request'}, status=400)


# Save new Topic
class SaveTopicView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            topic_name = request.data.get('topic_name')

            if not topic_name:
                return Response({'error': 'Topic Name is required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                state = request_handler.store_topic(topic_name)

                return Response({'message': 'Topic Processing: ', 'Status': state},
                                status=status.HTTP_200_OK)

            except ValueError:
                return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        try:
            # Call the get_all_device function
            all_topics = request_handler.get_all_topics()

            # Serialize the attendance details into a JSON response
            serialized_data = []
            for topic in all_topics:
                serialized_data.append({
                    'topic_id': topic.topic_id,
                    'topic_name': topic.topic_name
                })

            return JsonResponse({'all_topics': serialized_data}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Invalid request'}, status=400)


# Save new Device
class SaveDeviceView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            device_id = request.data.get('device_id')
            topic_id = request.data.get('topic_id')
            department_id = request.data.get('department_id')
            MAC_add = request.data.get('MAC')
            lock_status = request.data.get('lock_status')

            if not topic_id or not department_id or not device_id:
                return Response({'error': 'Topic, Device and Department are required'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                state = request_handler.store_device(device_id, topic_id, department_id, MAC_add, lock_status)

                return Response({'message': 'Department Processing: ', 'Status': state},
                                status=status.HTTP_200_OK)

            except ValueError:
                return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            # Call the get_all_device function
            all_devices = request_handler.get_all_devices()

            # Serialize the attendance details into a JSON response
            serialized_data = []
            for device in all_devices:

                topic_dict = model_to_dict(device.topic_id)
                department_dict = model_to_dict(device.department_id)

                serialized_data.append({
                    'device_id': device.device_id,
                    'department_data': department_dict,
                    'topic_data': topic_dict,
                    'MAC': device.MAC,
                    'lock_status': device.lock_status,

                })

            return JsonResponse({'all_devices': serialized_data}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Invalid request'}, status=400)


# Create New Employee Class
class EmployeeCreateView(APIView):
    def post(self, request, *args, **kwargs):

        department_name = request.data.get('departmentName')

        try:
            department_instance = Department.objects.get(department_name=department_name)

        except Department.DoesNotExist:
            return Response(f"No department found with the name {department_name}", status=404)

        employee = Employee.objects.create(
            first_name=request.data.get('firstName'),
            last_name=request.data.get('lastName'),
            gender=request.data.get('gender'),
            age=request.data.get('age'),
            contact_address=request.data.get('number'),
            emp_email=request.data.get('email'),
            department_id=department_instance
        )

        return Response({'message': 'Employee created successfully'}, status=status.HTTP_201_CREATED)


# Get Employee Details According to the email
class GetEmployeeDetailsView(APIView):
    def get(self, request, emp_email):
        try:

            # Call the get_attendance_details function
            emp_details = request_handler.get_emp_details(emp_email)

            # Serialize the attendance details into a JSON response
            serialized_data = []

            try:
                department_dict = model_to_dict(emp_details.department_id)
            except Department.DoesNotExist:
                department_dict = ''

            serialized_data.append({
                'first_name': emp_details.first_name,
                'last_name': emp_details.last_name,
                'gender': emp_details.gender,
                'age': emp_details.age,
                'contact_address': emp_details.contact_address,
                'department_id': department_dict,
            })

            return JsonResponse({'Emp_details': serialized_data}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Invalid emp_id or month'}, status=400)