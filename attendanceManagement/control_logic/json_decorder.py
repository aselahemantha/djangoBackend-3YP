import json
import os
from attendanceManagement.control_logic import input_attendance


def json_decorator(msg):
    payload = msg.payload.decode()
    try:
        json_payload = json.loads(payload)
        # Now `json_payload` is a Python dictionary containing the parsed JSON data
        # You can access values using keys, e.g., json_payload["key"]

        if json_payload.get("mode", "").lower() == "attendance":
            print("Attendance Marking Mode Activated")
            #input_attendance.add_attendance(payload)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")