from rest_framework import serializers

from .models import Case, CaseDocument, Deceased, FamilyMember


class DeceasedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deceased
        fields = [
            "id",
            "tenant",
            "branch",
            "first_name",
            "last_name",
            "id_number",
            "date_of_birth",
            "date_of_death",
            "place_of_death",
        ]
        read_only_fields = ["id", "tenant"]


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            "id",
            "tenant",
            "case",
            "first_name",
            "last_name",
            "relationship",
            "phone",
            "email",
            "is_next_of_kin",
        ]
        read_only_fields = ["id", "tenant"]


class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ["id", "tenant", "case", "document_type", "title", "file", "uploaded_by", "uploaded_at"]
        read_only_fields = ["id", "tenant", "uploaded_by", "uploaded_at"]


class CaseSerializer(serializers.ModelSerializer):
    deceased_detail = DeceasedSerializer(source="deceased", read_only=True)
    family_members = FamilyMemberSerializer(many=True, read_only=True)
    documents = CaseDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = [
            "id",
            "tenant",
            "branch",
            "deceased",
            "deceased_detail",
            "reference",
            "status",
            "service_date",
            "notes",
            "created_by",
            "created_at",
            "updated_at",
            "family_members",
            "documents",
        ]
        read_only_fields = ["id", "tenant", "created_by", "created_at", "updated_at"]
