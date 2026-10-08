from django.urls import path

from .views import (
    CertificateDownloadView,
    GenerationJobCreateView,
    GenerationJobStatusView,
    JobCertificatesView,
)


urlpatterns = [

    path(
        "jobs/",
        GenerationJobCreateView.as_view(),
        name="create-job",
    ),

    path(
        "jobs/<int:job_id>/",
        GenerationJobStatusView.as_view(),
        name="job-status",
    ),

    path(
        "jobs/<int:job_id>/certificates/",
        JobCertificatesView.as_view(),
        name="job-certificates",
    ),

    path(
        "certificates/<uuid:certificate_id>/download/",
        CertificateDownloadView.as_view(),
        name="certificate-download",
    ),
]