from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Certificate, GenerationJob
from .services import generate_single_certificate


@shared_task
def process_generation_job(job_id):

    try:
        job = GenerationJob.objects.get(
            id=job_id
        )
    except GenerationJob.DoesNotExist:
        return

    job.status = GenerationJob.Status.PROCESSING
    job.started_at = timezone.now()

    job.save(
        update_fields=[
            "status",
            "started_at",
        ]
    )

    certificates = job.certificates.all()

    for certificate in certificates:

        try:
            generate_single_certificate(
                certificate
            )

            GenerationJob.objects.filter(
                id=job.id
            ).update(
                successful_count=(
                    # Use DB value rather than stale
                    # Python object value.
                    job.successful_count + 1
                )
            )

            job.successful_count += 1

        except Exception as exc:

            certificate.status = (
                Certificate.Status.FAILED
            )

            certificate.error_message = str(exc)

            certificate.completed_at = (
                timezone.now()
            )

            certificate.save(
                update_fields=[
                    "status",
                    "error_message",
                    "completed_at",
                ]
            )

            GenerationJob.objects.filter(
                id=job.id
            ).update(
                failed_count=job.failed_count + 1
            )

            job.failed_count += 1

    job.completed_at = timezone.now()

    if job.failed_count == 0:
        job.status = GenerationJob.Status.COMPLETED

    elif job.successful_count > 0:
        job.status = (
            GenerationJob.Status.COMPLETED_WITH_ERRORS
        )

    else:
        job.status = GenerationJob.Status.FAILED

    job.save(
        update_fields=[
            "status",
            "successful_count",
            "failed_count",
            "completed_at",
        ]
    )