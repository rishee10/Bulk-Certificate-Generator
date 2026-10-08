from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from Certificate_app.models import Certificate, GenerationJob


class GenerationJobTests(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.valid_payload = {
            "event_name": "Python Workshop",
            "recipients": [
                {
                    "name": "Rahul Sharma",
                    "email": "rahul@example.com",
                    "course": "Python Development",
                },
                {
                    "name": "Priya Singh",
                    "email": "priya@example.com",
                    "course": "Python Development",
                },
            ],
        }

    @patch(
        "certificates.views.process_generation_job.delay"
    )
    def test_create_generation_job(
        self,
        mock_task
    ):

        response = self.client.post(
            "/api/jobs/",
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            202
        )

        self.assertIn(
            "job_id",
            response.data
        )

        self.assertEqual(
            response.data["total"],
            2
        )

        self.assertTrue(
            GenerationJob.objects.exists()
        )

        self.assertEqual(
            Certificate.objects.count(),
            2
        )

        mock_task.assert_called_once()

    def test_empty_recipients_is_invalid(self):

        payload = {
            "event_name": "Python Workshop",
            "recipients": [],
        }

        response = self.client.post(
            "/api/jobs/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_invalid_email_is_rejected(self):

        payload = {
            "event_name": "Python Workshop",
            "recipients": [
                {
                    "name": "Rahul Sharma",
                    "email": "invalid-email",
                    "course": "Python",
                }
            ],
        }

        response = self.client.post(
            "/api/jobs/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_job_status(self):

        job = GenerationJob.objects.create(
            event_name="Python Workshop",
            total_count=2,
            successful_count=1,
            failed_count=1,
            status=(
                GenerationJob.Status
                .COMPLETED_WITH_ERRORS
            ),
        )

        response = self.client.get(
            f"/api/jobs/{job.id}/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["total_count"],
            2
        )

        self.assertEqual(
            response.data["successful_count"],
            1
        )

        self.assertEqual(
            response.data["failed_count"],
            1
        )

        self.assertEqual(
            response.data["progress"],
            100
        )