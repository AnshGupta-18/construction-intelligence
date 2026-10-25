
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from modules.database import get_connection, initialize_database


def generate_project_report():
    initialize_database()
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "Construction Intelligence Platform",
            styles["Title"],
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        Paragraph("Construction Project Report", styles["Heading2"])
    )
    story.append(Paragraph(
        f"Report generated: {pd.Timestamp.now().strftime('%d %b %Y, %I:%M %p')}",
        styles["Normal"],
    ))
    story.append(Spacer(1, 18))

    with get_connection() as conn:
        tasks = conn.execute("""
            SELECT name, duration, priority, start_date, status, predecessor
            FROM tasks ORDER BY id
        """).fetchall()

        costs = conn.execute("""
            SELECT item_name, material_cost, labour_cost,
                   equipment_cost, contingency, total_cost
            FROM cost_items ORDER BY id
        """).fetchall()

    story.append(Paragraph("1. Project Schedule", styles["Heading2"]))

    if tasks:
        task_data = [[
            "Task", "Days", "Priority", "Start Date", "Status", "Depends On"
        ]]
        for task in tasks:
            task_data.append([
                str(task[0]),
                str(task[1]),
                str(task[2]),
                str(task[3]),
                str(task[4]),
                str(task[5] or "-"),
            ])

        task_table = Table(
            task_data,
            repeatRows=1,
            colWidths=[1.45*inch, 0.45*inch, 0.65*inch,
                       0.85*inch, 0.75*inch, 1.0*inch],
        )
        task_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234E70")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F0F4F8")]),
        ]))
        story.append(task_table)
    else:
        story.append(Paragraph("No project tasks have been added.", styles["Normal"]))

    story.append(Spacer(1, 20))
    story.append(Paragraph("2. Cost Estimate", styles["Heading2"]))

    if costs:
        cost_data = [[
            "Item", "Materials (Rs.)", "Labour (Rs.)",
            "Equipment (Rs.)", "Contingency (Rs.)", "Total (Rs.)"
        ]]

        for cost in costs:
            cost_data.append([
                str(cost[0]),
                f"{cost[1]:,.2f}",
                f"{cost[2]:,.2f}",
                f"{cost[3]:,.2f}",
                f"{cost[4]:,.2f}",
                f"{cost[5]:,.2f}",
            ])

        grand_total = sum(float(cost[5]) for cost in costs)
        cost_data.append([
            "GRAND TOTAL", "", "", "", "", f"{grand_total:,.2f}"
        ])

        cost_table = Table(
            cost_data,
            repeatRows=1,
            colWidths=[1.25*inch, 0.9*inch, 0.75*inch,
                       0.85*inch, 0.95*inch, 0.85*inch],
        )
        cost_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234E70")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, -1), (-1, -1),
             colors.HexColor("#DCE6F1")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))
        story.append(cost_table)
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            f"<b>Estimated Total Project Cost: Rs. {grand_total:,.2f}</b>",
            styles["Heading3"],
        ))
    else:
        story.append(Paragraph("No cost items have been added.", styles["Normal"]))

    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "Note: This report is based on the project tasks and cost estimates "
        "currently saved in the application database.",
        styles["Italic"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def render_pdf_reports():
    st.subheader("📄 Download Project Report")
    st.write(
        "Generate a PDF containing your saved construction schedule "
        "and cost estimates."
    )

    if st.button("Generate PDF Report"):
        try:
            pdf_bytes = generate_project_report()
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name="construction_project_report.pdf",
                mime="application/pdf",
            )
        except Exception as error:
            st.error(f"Could not generate the report: {error}")
