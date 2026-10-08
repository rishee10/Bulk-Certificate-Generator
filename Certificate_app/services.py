from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from .generators import generate_certificate_pdf
from .models import Certificate, GenerationJob


def create_generation_job(
    event_name,
    recipients
):
    """
    Create a generation job and all certificate records.
    """

    with transaction.atomic():

        job = GenerationJob.objects.create(
            event_name=event_name,
            total_count=len(recipients),
            status=GenerationJob.Status.QUEUED
        )

        certificates = []

        for recipient in recipients:

            certificate = Certificate(
                job=job,
                recipient_name=recipient["name"],
                recipient_email=recipient["email"],
                course_name=recipient["course"],
                status=Certificate.Status.PENDING
            )

            certificates.append(certificate)

        Certificate.objects.bulk_create(
            certificates
        )

    return job


def generate_single_certificate(
    certificate
):
    """
    Generate and save one certificate.

    Raises:
        Exception: if certificate generation fails.
    """

    certificate.status = (
        Certificate.Status.PROCESSING
    )

    certificate.save(
        update_fields=["status"]
    )

    pdf_buffer = generate_certificate_pdf(
        recipient_name=certificate.recipient_name,
        course_name=certificate.course_name,
        event_name=certificate.job.event_name,
        certificate_id=str(certificate.id),
    )

    filename = (
        f"{certificate.recipient_name}"
        .replace(" ", "_")
        + "_certificate.pdf"
    )

    certificate.file.save(
        filename,
        ContentFile(pdf_buffer.read()),
        save=False
    )

    certificate.status = (
        Certificate.Status.COMPLETED
    )

    certificate.completed_at = timezone.now()

    certificate.error_message = None

    certificate.save()

    return certificate