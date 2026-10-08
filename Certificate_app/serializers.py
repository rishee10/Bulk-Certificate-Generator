from rest_framework import serializers

from .models import Certificate, GenerationJob


class RecipientSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=255
    )

    email = serializers.EmailField()

    course = serializers.CharField(
        max_length=255
    )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Name cannot be empty."
            )

        return value

    def validate_course(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Course cannot be empty."
            )

        return value


class CreateGenerationJobSerializer(
    serializers.Serializer
):

    event_name = serializers.CharField(
        max_length=255
    )

    recipients = RecipientSerializer(
        many=True
    )

    def validate_event_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Event name cannot be empty."
            )

        return value

    def validate_recipients(self, value):

        if not value:
            raise serializers.ValidationError(
                "At least one recipient is required."
            )

        if len(value) > 1000:
            raise serializers.ValidationError(
                "Maximum 1000 recipients are allowed per job."
            )

        return value


class CertificateSerializer(
    serializers.ModelSerializer
):

    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate

        fields = [
            "id",
            "recipient_name",
            "recipient_email",
            "course_name",
            "status",
            "error_message",
            "download_url",
            "created_at",
            "completed_at",
        ]

    def get_download_url(self, obj):

        if not obj.file:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.file.url
            )

        return obj.file.url


class JobStatusSerializer(
    serializers.ModelSerializer
):

    progress = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = GenerationJob

        fields = [
            "id",
            "event_name",
            "status",
            "total_count",
            "successful_count",
            "failed_count",
            "progress",
            "created_at",
            "started_at",
            "completed_at",
        ]