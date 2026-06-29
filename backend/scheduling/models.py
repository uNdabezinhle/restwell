from django.conf import settings
from django.db import models


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        VEHICLE = "vehicle", "Vehicle"
        STAFF = "staff", "Staff"
        VENUE = "venue", "Venue"
        EQUIPMENT = "equipment", "Equipment"

    tenant = models.ForeignKey("tenants.Tenant", related_name="resources", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="resources", on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    resource_type = models.CharField(max_length=30, choices=ResourceType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["resource_type", "name"]

    def __str__(self):
        return self.name


class CalendarEvent(models.Model):
    class EventType(models.TextChoices):
        FUNERAL_SERVICE = "funeral_service", "Funeral Service"
        PICKUP = "pickup", "Pickup"
        MEETING = "meeting", "Meeting"
        OTHER = "other", "Other"

    tenant = models.ForeignKey("tenants.Tenant", related_name="calendar_events", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="calendar_events", on_delete=models.PROTECT)
    case = models.ForeignKey("cases.Case", related_name="calendar_events", null=True, blank=True, on_delete=models.PROTECT)
    title = models.CharField(max_length=180)
    event_type = models.CharField(max_length=40, choices=EventType.choices, default=EventType.OTHER)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=180, blank=True)
    resources = models.ManyToManyField(Resource, related_name="calendar_events", blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title
