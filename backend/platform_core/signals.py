from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .middleware import get_current_audit_user
from .models import AuditLog, ConsentRecord, DataSubjectRequest, TenantFeature
from .services import write_audit_log


IGNORED_MODELS = {AuditLog}
TRACKED_APPS = {
    "accounts",
    "branded_apps",
    "branding",
    "cases",
    "financials",
    "geolocation",
    "inventory",
    "mortuary",
    "notifications",
    "onboarding",
    "platform_core",
    "policies",
    "scheduling",
    "tenants",
    "website_builder",
}


@receiver(post_save)
def audit_saved_model(sender, instance, created, **kwargs):
    if sender in IGNORED_MODELS or sender._meta.app_label not in TRACKED_APPS:
        return
    action = AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE
    write_audit_log(action=action, resource=instance, actor=get_current_audit_user())


@receiver(post_delete)
def audit_deleted_model(sender, instance, **kwargs):
    if sender in IGNORED_MODELS or sender._meta.app_label not in TRACKED_APPS:
        return
    write_audit_log(action=AuditLog.Action.DELETE, resource=instance, actor=get_current_audit_user())
