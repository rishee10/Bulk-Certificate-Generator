import uuid

from django.db import models


class GenerationJob(models.Model):

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        COMPLETED_WITH_ERRORS = (
            "completed_with_errors",
            "Completed With Errors",
        )
        FAILED = "failed", "Failed"

    event_name = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.QUEUED
    )

    total_count = models.PositiveIntegerField(
        default=0
    )

    successful_count = models.PositiveIntegerField(
        default=0
    )

    failed_count = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Job #{self.id} - {self.event_name}"

    @property
    def progress(self):
        if self.total_count == 0:
            return 0

        processed = (
            self.successful_count +
            self.failed_count
        )

        return int(
            processed * 100 / self.total_count
        )


class Certificate(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    job = models.ForeignKey(
        GenerationJob,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    recipient_name = models.CharField(
        max_length=255
    )

    recipient_email = models.EmailField()

    course_name = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    file = models.FileField(
        upload_to="certificates/",
        null=True,
        blank=True
    )

    error_message = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.recipient_name} - "
            f"{self.course_name}"
        )