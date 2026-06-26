from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    legal_name = models.CharField(max_length=220, blank=True)
    registration_number = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Branch(models.Model):
    tenant = models.ForeignKey(Tenant, related_name="branches", on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    code = models.CharField(max_length=40)
    province = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="unique_branch_code_per_tenant"),
        ]

    def __str__(self):
        return f"{self.tenant}: {self.name}"
