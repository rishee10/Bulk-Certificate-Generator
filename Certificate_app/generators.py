from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def generate_certificate_pdf(
    recipient_name,
    course_name,
    event_name,
    certificate_id,
):
    """
    Generate one certificate PDF.

    Returns:
        BytesIO: PDF file in memory.
    """

    buffer = BytesIO()

    width, height = A4

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    # Border
    margin = 15 * mm

    pdf.setStrokeColor(
        colors.HexColor("#1F4E79")
    )

    pdf.setLineWidth(3)

    pdf.rect(
        margin,
        margin,
        width - 2 * margin,
        height - 2 * margin
    )

    # Organization
    pdf.setFont(
        "Helvetica-Bold",
        26
    )

    pdf.drawCentredString(
        width / 2,
        height - 55 * mm,
        "CERTIFICATE OF COMPLETION"
    )

    # Event
    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        width / 2,
        height - 72 * mm,
        event_name
    )

    # Award text
    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        width / 2,
        height - 95 * mm,
        "This certificate is proudly presented to"
    )

    # Recipient
    pdf.setFont(
        "Helvetica-Bold",
        28
    )

    pdf.drawCentredString(
        width / 2,
        height - 115 * mm,
        recipient_name
    )

    # Course
    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        width / 2,
        height - 140 * mm,
        "for successfully completing"
    )

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawCentredString(
        width / 2,
        height - 153 * mm,
        course_name
    )

    # Certificate ID
    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        margin + 10 * mm,
        margin + 10 * mm,
        f"Certificate ID: {certificate_id}"
    )

    pdf.showPage()

    pdf.save()

    buffer.seek(0)

    return buffer