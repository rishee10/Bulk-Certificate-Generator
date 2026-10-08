from unittest.mock import patch

from django.core.files.base import ContentFile
from django.test import TestCase

from Certificate_app.generators import (
    generate_certificate_pdf,
)
from Certificate_app.models import (
    Certificate,
    GenerationJob,
)
from Certificate_app.tasks import (
    process_generation_job,
)


class CertificateGenerationTests(TestCase):

    def test_certificate_pdf_generation(self):

        pdf = generate_certificate_pdf(
            recipient_name="Rahul Sharma",
            course_name="Python Development",
            event_name="Python Workshop",
            certificate_id="TEST-001",
        )

        content = pdf.read()

        self.assertTrue(
            content.startswith(b"%PDF")
        )

        self.assertGreater(
            len(content),
            100
        )

    @patch(
        "certificates.tasks.generate_single_certificate"
    )
    def test_individual_certificate_failure(
        self,
        mock_generate
    ):

        job = GenerationJob.objects.create(
            event_name="Python Workshop",
            total_count=3,
        )

        certificate_1 = Certificate.objects.create(
            job=job,
            recipient_name="Rahul",
            recipient_email="rahul@example.com",
            course_name="Python",
        )

        certificate_2 = Certificate.objects.create(
            job=job,
            recipient_name="Priya",
            recipient_email="priya@example.com",
            course_name="Python",
        )

        certificate_3 = Certificate.objects.create(
            job=job,
            recipient_name="Amit",
            recipient_email="amit@example.com",
            course_name="Python",
        )

        def side_effect(certificate):

            if certificate.id == certificate_2.id:
                raise Exception(
                    "PDF generation failed"
                )

            certificate.status = (
                Certificate.Status.COMPLETED
            )

            certificate.save()

        mock_generate.side_effect = side_effect

        process_generation_job(
            job.id
        )

        job.refresh_from_db()

        certificate_1.refresh_from_db()
        certificate_2.refresh_from_db()
        certificate_3.refresh_from_db()

        self.assertEqual(
            certificate_1.status,
            Certificate.Status.COMPLETED
        )

        self.assertEqual(
            certificate_2.status,
            Certificate.Status.FAILED
        )

        self.assertEqual(
            certificate_3.status,
            Certificate.Status.COMPLETED
        )

        self.assertEqual(
            job.successful_count,
            2
        )

        self.assertEqual(
            job.failed_count,
            1
        )

        self.assertEqual(
            job.status,
            GenerationJob.Status.COMPLETED_WITH_ERRORS
        )