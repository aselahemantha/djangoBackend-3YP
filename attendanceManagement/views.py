import json
import os
import time
import  base64

from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from attendanceManagement.models import Face_Data, Employee, Fingerprint_Data
from attendanceManagement.mqtt import publish_msg
from attendanceManagement.control_logic import request_handler
from django.conf import settings
from attendanceManagement.face_detection import recognize_faces_image, encode_faces
from attendanceManagement.control_logic import request_handler


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

            # Save the image to the specified path using the upload_to function
            face_data = Face_Data(emp_id=employee, face=image_file)
            face_data.save()

            # Get the saved image path
            image_path = face_data.face.url

            return Response({'message': 'Image saved successfully', 'image_path': image_path},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
