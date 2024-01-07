import json
import time

from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from attendanceManagement.mqtt import publish_msg
from attendanceManagement.control_logic import input_attendance

class HomeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Welcome to the JWT Authentication page using React Js and Django!'}
        return Response(content)


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


class ConfigureDeviceView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            publish_msg.run(request.data)

            return Response({'message': 'Configuration sent to MQTT'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Failed to send configuration to MQTT: {e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActiveDeviceView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            publish_msg.run(request.data)

            return Response({'message': 'Activation sent to MQTT'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Failed to send activation to MQTT: {e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceView(APIView):

    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON format in request body'}, status=status.HTTP_400_BAD_REQUEST)

        if not all(key in data for key in ['id', 'sl', 'cmd']):
            return Response({'error': 'Missing required fields in the request data'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            output = input_attendance.process_attendance_data(data)
            return Response({'message': output}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

