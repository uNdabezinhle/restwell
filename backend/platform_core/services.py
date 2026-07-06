from .models import AuditLog, TenantFeature


def feature_enabled(tenant, code):
    if tenant is None:
        return True
    feature = TenantFeature.objects.filter(tenant=tenant, code=code).first()
    return True if feature is None else feature.is_enabled


def write_audit_log(*, action, resource, actor=None, tenant=None, description="", metadata=None):
    if resource.__class__.__name__ == "AuditLog":
        return None
    tenant = tenant or getattr(resource, "tenant", None)
    return AuditLog.objects.create(
        tenant=tenant,
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        resource_type=f"{resource.__class__.__module__}.{resource.__class__.__name__}",
        resource_id=str(getattr(resource, "pk", "")),
        description=description,
        metadata=metadata or {},
    )
