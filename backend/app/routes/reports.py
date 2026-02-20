from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
import os

router = APIRouter(prefix="/reports", tags=["Reports"])

PDF_PATH = "wealth_report.pdf"

@router.get("/wealth/pdf")
def generate_wealth_pdf():
    c = canvas.Canvas(PDF_PATH)
    c.drawString(100, 750, "Wealth Report")
    c.drawString(100, 720, "Total Wealth: ")
    c.save()

    return FileResponse(
        path=PDF_PATH,
        filename="wealth_report.pdf",
        media_type="application/pdf"
    )
