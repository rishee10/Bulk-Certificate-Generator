from django.contrib import admin

from .models import Certificate, GenerationJob


@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "event_name",
        "status",
        "total_count",
        "successful_count",
        "failed_count",
        "created_at",
    ]

    list_filter = [
        "status",
        "created_at",
    ]

    search_fields = [
        "event_name",
    ]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "recipient_name",
        "recipient_email",
        "course_name",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
    ]

    search_fields = [
        "recipient_name",
        "recipient_email",
        "course_name",
    ]