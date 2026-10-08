from io import BytesIO

from django.core.files.base import ContentFile
from django.test import TestCase
from rest_framework.test import APIClient

from Certificate_app.models import (
    Certificate,
    GenerationJob,
)


class CertificateRetrievalTests(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.job = GenerationJob.objects.create(
            event_name="Python Workshop",
            total_count=1,
            successful_count=1,
            status=GenerationJob.Status.COMPLETED,
        )

        self.certificate = Certificate.objects.create(
            job=self.job,
            recipient_name="Rahul Sharma",
            recipient_email="rahul@example.com",
            course_name="Python Development",
            status=Certificate.Status.COMPLETED,
        )

        self.certificate.file.save(
            "test_certificate.pdf",
            ContentFile(
                b"%PDF-1.4 test certificate"
            )
        )

    def test_list_job_certificates(self):

        response = self.client.get(
            f"/api/jobs/{self.job.id}/certificates/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]["recipient_name"],
            "Rahul Sharma"
        )

    def test_download_certificate(self):

        response = self.client.get(
            "/api/certificates/"
            f"{self.certificate.id}/download/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf"
        )

    def test_failed_certificate_cannot_be_downloaded(self):

        self.certificate.status = (
            Certificate.Status.FAILED
        )

        self.certificate.error_message = (
            "Generation failed"
        )

        self.certificate.save()

        response = self.client.get(
            "/api/certificates/"
            f"{self.certificate.id}/download/"
        )

        self.assertEqual(
            response.status_code,
            404
        )