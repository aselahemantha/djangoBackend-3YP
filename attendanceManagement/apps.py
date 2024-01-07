from django.apps import AppConfig


class AttendanceManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendanceManagement'

    def ready(self):
        from attendanceManagement.mqtt import subscribe_mqtt
        subscribe_mqtt.start_mqtt_thread()
