from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO


def generate_wealth_report(user, investments, goals):
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    # 🔹 Title
    elements.append(Paragraph("Personal Wealth Report", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    # 🔹 User Info
    elements.append(Paragraph(f"<b>Name:</b> {user['name']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Email:</b> {user['email']}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # 🔹 Investment Summary
    total_investment = sum(inv["amount"] for inv in investments)

    elements.append(
        Paragraph(
            f"<b>Total Investment:</b> ₹{total_investment}",
            styles["Heading2"]
        )
    )
    elements.append(Spacer(1, 0.2 * inch))

    # 🔹 Goals Section
    elements.append(Paragraph("Goals Progress", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    # 🔹 Goals Table
    table_data = [
        ["Goal Name", "Target Amount", "Saved Amount", "Progress %"]
    ]

    for goal in goals:
        progress = (
            round((goal["saved"] / goal["target"]) * 100, 2)
            if goal["target"] > 0 else 0
        )

        table_data.append([
            goal["name"],
            f"₹{goal['target']}",
            f"₹{goal['saved']}",
            f"{progress}%",
        ])

    table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    elements.append(table)

    # 🔹 Build PDF
    pdf.build(elements)
    buffer.seek(0)

    return buffer
