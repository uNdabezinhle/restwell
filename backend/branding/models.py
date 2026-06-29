from django.db import models


class TenantBranding(models.Model):
    tenant = models.OneToOneField("tenants.Tenant", related_name="branding", on_delete=models.CASCADE)
    logo = models.FileField(upload_to="branding/logos/", blank=True)
    primary_color = models.CharField(max_length=7, default="#0F766E")
    secondary_color = models.CharField(max_length=7, default="#2563EB")
    email_from_name = models.CharField(max_length=120, blank=True)
    sms_sender_name = models.CharField(max_length=40, blank=True)
    custom_domain = models.CharField(max_length=180, blank=True)
    remove_powered_by = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant__name"]

    def __str__(self):
        return f"{self.tenant} branding"
