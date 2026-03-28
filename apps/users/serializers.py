from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "currency_default", "document_type", "document_number", "date_joined",
        )
        read_only_fields = ("id", "username", "email", "date_joined")


class DocumentMetadataSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=User.DOCUMENT_TYPE_CHOICES)
    document_number = serializers.CharField(max_length=20, min_length=5)
