from django.conf import settings
from django.db import models


class Deceased(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", related_name="deceased_records", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="deceased_records", on_delete=models.PROTECT)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    id_number = models.CharField(max_length=40, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    place_of_death = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Case(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    tenant = models.ForeignKey("tenants.Tenant", related_name="cases", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="cases", on_delete=models.PROTECT)
    deceased = models.ForeignKey(Deceased, related_name="cases", on_delete=models.PROTECT)
    reference = models.CharField(max_length=40)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
    service_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "reference"], name="unique_case_reference_per_tenant"),
        ]

    def __str__(self):
        return self.reference


class FamilyMember(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", related_name="family_members", on_delete=models.CASCADE)
    case = models.ForeignKey(Case, related_name="family_members", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    relationship = models.CharField(max_length=80)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    is_next_of_kin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_next_of_kin", "last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class CaseDocument(models.Model):
    class DocumentType(models.TextChoices):
        BI1663 = "bi1663", "BI1663"
        COC = "coc", "Certificate of Competence"
        ID_COPY = "id_copy", "ID Copy"
        OTHER = "other", "Other"

    tenant = models.ForeignKey("tenants.Tenant", related_name="case_documents", on_delete=models.CASCADE)
    case = models.ForeignKey(Case, related_name="documents", on_delete=models.CASCADE)
    document_type = models.CharField(max_length=32, choices=DocumentType.choices, default=DocumentType.OTHER)
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="case-documents/%Y/%m/", blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title
