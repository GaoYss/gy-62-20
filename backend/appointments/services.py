from django.utils.dateparse import parse_datetime

from backend.residents.models import Resident
from backend.residents.services import serialize_resident

from .models import Appointment


VALID_TRANSITIONS = {
    "pending": ["approved", "rejected", "cancelled"],
    "approved": ["completed", "cancelled"],
    "rejected": [],
    "completed": [],
    "cancelled": [],
}

TERMINAL_STATUSES = {"completed", "cancelled", "rejected"}

WRITE_FIELDS = [
    "resident",
    "resident_id",
    "family_name",
    "family_phone",
    "relationship",
    "visit_time",
    "visitor_count",
    "status",
    "notes",
]


class StatusTransitionError(Exception):
    pass


def validate_status_transition(current_status, new_status):
    if current_status == new_status:
        return
    if current_status in TERMINAL_STATUSES:
        raise StatusTransitionError(
            f"当前状态为「{Appointment.STATUS_CHOICES[[s[0] for s in Appointment.STATUS_CHOICES].index(current_status)][1]}」，不允许再变更状态"
        )
    if new_status not in VALID_TRANSITIONS.get(current_status, []):
        allowed = VALID_TRANSITIONS.get(current_status, [])
        allowed_names = [
            Appointment.STATUS_CHOICES[[s[0] for s in Appointment.STATUS_CHOICES].index(s)][1]
            for s in allowed
        ]
        if allowed_names:
            raise StatusTransitionError(
                f"状态流转不合法：仅允许从「{Appointment.STATUS_CHOICES[[s[0] for s in Appointment.STATUS_CHOICES].index(current_status)][1]}」变更为 {', '.join(allowed_names)}"
            )
        else:
            raise StatusTransitionError(
                f"状态流转不合法：当前状态「{Appointment.STATUS_CHOICES[[s[0] for s in Appointment.STATUS_CHOICES].index(current_status)][1]}」不允许变更"
            )
    if current_status == "completed":
        raise StatusTransitionError("已完成的预约不可再次取消或变更状态")


def serialize_appointment(appointment):
    return {
        "id": appointment.id,
        "resident": serialize_resident(appointment.resident),
        "resident_id": appointment.resident_id,
        "family_name": appointment.family_name,
        "family_phone": appointment.family_phone,
        "relationship": appointment.relationship,
        "visit_time": appointment.visit_time.isoformat(),
        "visitor_count": appointment.visitor_count,
        "status": appointment.status,
        "notes": appointment.notes,
        "created_at": appointment.created_at.isoformat(),
        "updated_at": appointment.updated_at.isoformat(),
    }


def normalize_payload(payload):
    data = {field: payload.get(field) for field in WRITE_FIELDS if field in payload}
    if "resident" in data:
        data["resident_id"] = data.pop("resident")
    if "visit_time" in data and isinstance(data["visit_time"], str):
        data["visit_time"] = parse_datetime(data["visit_time"])
    return data


def list_appointments(status=None):
    queryset = Appointment.objects.select_related("resident")
    if status:
        queryset = queryset.filter(status=status)
    return [serialize_appointment(item) for item in queryset]


def create_appointment(payload):
    data = normalize_payload(payload)
    Resident.objects.get(pk=data["resident_id"])
    return Appointment(**data)


def update_appointment(appointment, payload):
    data = normalize_payload(payload)
    if "status" in data and data["status"] != appointment.status:
        validate_status_transition(appointment.status, data["status"])
    if appointment.status in TERMINAL_STATUSES:
        for field in ["resident", "resident_id", "family_name", "family_phone", "relationship", "visit_time", "visitor_count"]:
            data.pop(field, None)
    for field, value in data.items():
        setattr(appointment, field, value)
    appointment.save()
    return appointment


def cancel_appointment(appointment):
    if appointment.status == "completed":
        raise StatusTransitionError("已完成的预约不可再次取消")
    validate_status_transition(appointment.status, "cancelled")
    appointment.status = "cancelled"
    appointment.save()
    return appointment
