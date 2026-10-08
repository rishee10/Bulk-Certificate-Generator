# Bulk Certificate Generator

A Django REST API that generates certificates in bulk from a predefined PDF template. It accepts multiple recipients in a single request, processes certificates in the background, tracks job progress, and provides individual certificate download links.

## What It Does

- Accepts multiple recipients in one API request.
- Validates recipient name, email, and course.
- Creates a bulk certificate generation job.
- Generates individual PDF certificates.
- Processes certificates using Celery in the background.
- Tracks job status and progress.
- If one certificate fails, other certificates continue processing.
- Provides a download URL for each successfully generated certificate.

## How It Works

```text
Client
  ↓
POST /api/jobs/
  ↓
Django REST API
  ↓
Create Generation Job + Certificates
  ↓
Celery + Redis
  ↓
Generate PDF Certificates
  ↓
Save PDFs + Update Status
  ↓
GET /api/jobs/<id>/certificates/
  ↓
Download Certificate
```

## Tech Stack

- **Python**
- **Django**
- **Django REST Framework**
- **Celery** – background certificate processing
- **Redis** – Celery message broker
- **ReportLab** – PDF certificate generation
- **SQLite** – relational database
- **Docker** – Redis container

## Project Structure

```text
Certificate_Generator/
│
├── Certificate_Generator/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── ...
│
├── Certificate_app/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── tasks.py
│   ├── services.py
│   ├── generators.py
│   ├── urls.py
│   └── tests/
│
├── manage.py
├── requirements.txt
└── README.md
```

## How to Run

### 1. Clone the project

```bash
git clone <your-repository-url>
cd Certificate_Generator
```

### 2. Create and activate virtual environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start Redis

Make sure Docker Desktop is running, then:

```bash
docker start certificate-redis
```

If the container does not exist:

```bash
docker run --name certificate-redis -p 6379:6379 -d redis
```

### 6. Start Celery

Open a new terminal:

```powershell
.\venv\Scripts\Activate.ps1
python -m celery -A Certificate_Generator.celery worker --loglevel=info --pool=solo
```

### 7. Start Django

Open another terminal:

```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

API will be available at:

```text
http://127.0.0.1:8000/
```

## Main API Endpoints

### Create Bulk Generation Job

```http
POST /api/jobs/
```

Example:

```json
{
    "event_name": "Python Workshop 2026",
    "recipients": [
        {
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "course": "Python Development"
        },
        {
            "name": "Priya Singh",
            "email": "priya@example.com",
            "course": "Python Development"
        }
    ]
}
```

### Check Job Status

```http
GET /api/jobs/<job_id>/
```

Returns:

- Job status
- Total certificates
- Successful certificates
- Failed certificates
- Progress percentage

### Get Generated Certificates

```http
GET /api/jobs/<job_id>/certificates/
```

Returns certificate information and download URLs.

### Download Certificate

```http
GET /api/certificates/<certificate_id>/download/
```

## Screenshots

### 1. Create Bulk Job

_Add screenshot of POST `/api/jobs/` response here._

```text
[ Screenshot: Create Job API ]
```

### 2. Job Status

_Add screenshot showing completed job and progress._

```text
[ Screenshot: Job Status API ]
```

### 3. Generated Certificates

_Add screenshot showing certificates with `download_url`._

```text
[ Screenshot: Certificate List API ]
```

### 4. Generated Certificate

_Add screenshot of the generated PDF certificate._

```text
[ Screenshot: Generated Certificate PDF ]
```

## Key Design Choice

The system uses **Celery + Redis** so certificate generation happens asynchronously. Each certificate is processed independently, so a failure for one recipient does not stop the remaining certificates from being generated.
