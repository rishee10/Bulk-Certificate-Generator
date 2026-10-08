from django.shortcuts import render

from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Certificate, GenerationJob
from .serializers import (
    CertificateSerializer,
    CreateGenerationJobSerializer,
    JobStatusSerializer,
)
from .services import create_generation_job
from .tasks import process_generation_job


class GenerationJobCreateView(APIView):

    def post(self, request):

        serializer = CreateGenerationJobSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        job = create_generation_job(
            event_name=serializer.validated_data[
                "event_name"
            ],
            recipients=serializer.validated_data[
                "recipients"
            ],
        )

        process_generation_job.delay(
            job.id
        )

        return Response(
            {
                "job_id": job.id,
                "status": job.status,
                "total": job.total_count,
                "message": (
                    "Certificate generation job "
                    "created successfully."
                ),
            },
            status=status.HTTP_202_ACCEPTED
        )


class GenerationJobStatusView(APIView):

    def get(self, request, job_id):

        job = get_object_or_404(
            GenerationJob,
            id=job_id
        )

        serializer = JobStatusSerializer(
            job
        )

        return Response(
            serializer.data
        )


class JobCertificatesView(APIView):

    def get(self, request, job_id):

        job = get_object_or_404(
            GenerationJob,
            id=job_id
        )

        certificates = job.certificates.all()

        serializer = CertificateSerializer(
            certificates,
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data
        )


class CertificateDownloadView(APIView):

    def get(self, request, certificate_id):

        certificate = get_object_or_404(
            Certificate,
            id=certificate_id
        )

        if certificate.status != (
            Certificate.Status.COMPLETED
        ):
            return Response(
                {
                    "error": (
                        "Certificate is not available."
                    ),
                    "status": certificate.status,
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not certificate.file:
            return Response(
                {
                    "error": (
                        "Certificate file does not exist."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            certificate.file.open("rb"),
            as_attachment=True,
            filename=(
                f"{certificate.recipient_name}"
                .replace(" ", "_")
                + "_certificate.pdf"
            ),
            content_type="application/pdf",
        )