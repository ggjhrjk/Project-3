import os
from datetime import datetime
from tkinter import messagebox
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from database.db import get_connection

LOGO_PATH = "assets/logo.png"

def watermark(canv, doc):
    try:
        canv.saveState()
        w, h = A4
        canv.setFillAlpha(0.15)
        canv.drawImage(LOGO_PATH, (w - 16*cm)/2, (h - 12*cm)/2, 16*cm, 12*cm, mask='auto')
        canv.restoreState()
    except Exception as e:
        print("PDF Watermark error:", e)

def add_page_number(canv, doc):
    canv.saveState()
    w, h = A4
    page_text = str(doc.page)
    canv.setFont("Helvetica", 10)
    text_width = canv.stringWidth(page_text, "Helvetica", 10)
    canv.drawString((w - text_width) / 2, 1*cm, page_text)
    canv.restoreState()

def create_full_bill_pdf(path, bill_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.id, p.id, p.name, p.age, p.gender, p.mobile, p.disease, p.image,
               b.total, b.paid, b.balance
        FROM bill b
        JOIN patient p ON b.patient_id = p.id
        WHERE b.id=?
    """, (bill_id,))
    b = cur.fetchone()

    if not b:
        conn.close()
        messagebox.showerror("Error", "Bill not found!")
        return

    (bid, pid, pname, age, gender, mobile, disease, img, total, paid, balance) = b

    cur.execute("""
        SELECT a.id, a.date, a.from_time, a.to_time, a.notes,
               d.name, d.id, d.mobile, d.department
        FROM appointment a
        JOIN doctor d ON a.doctor_id = d.id
        WHERE a.patient_id=?
        ORDER BY a.id DESC LIMIT 1
    """, (pid,))
    ap = cur.fetchone()

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4)
    elements = []

    try:
        logo_img = RLImage(LOGO_PATH, width=4*cm, height=4*cm)
    except:
        logo_img = Paragraph("", styles['Normal'])

    hospital_name = Paragraph("<b><font size=30 color=#003366>Naveen Care Hospital</font></b>", styles['Title'])
    address = Paragraph("<font size=15>45, Perumalpatti, East Street, Srivilliputtur<br/><br/>Phone: 9876543210</font>", styles['Normal'])

    header_table = Table([[logo_img, hospital_name], ['', address]], colWidths=[4*cm, 12*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'LEFT'),
        ('ALIGN', (1,1), (1,1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0)
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 20))

    today_date = datetime.now().strftime("%d/%m/%Y")
    date_para = Paragraph(f"<b><font size=14>Date: {today_date}</font></b>", styles['Normal'])
    date_table = Table([[date_para]], colWidths=[16*cm])
    date_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'RIGHT')]))
    elements.append(date_table)

    elements.append(Paragraph("<b><font size=18>BILL RECEIPT</font></b>", styles['Title']))
    elements.append(Spacer(1, 20))

    patient_lines = [
        f"Bill ID: {bid}",
        f"Patient Name: {pname} (ID: {pid})",
        f"Age: {age} | Gender: {gender}",
        f"Mobile: {mobile}",
        f"Disease: {disease}"
    ]
    for line in patient_lines:
        elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 8))

    elements.append(Spacer(1, 15))

    if ap:
        (aid, date, ft, tt, notes, dname, did, dmob, dept) = ap
        app_lines = [
            f"Appointment ID: {aid}",
            f"Doctor: {dname} (ID: {did}) - {dept}",
            f"Date & Time: {date} [{ft} - {tt}]",
            f"Notes: {notes}"
        ]
        for line in app_lines:
            elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 8))

    elements.append(Spacer(1, 20))

    cur.execute("SELECT item_name, amount FROM bill_items WHERE bill_id=?", (bill_id,))
    items = cur.fetchall()

    data = [["Item Name", "Amount (₹)"]]
    for item in items:
        data.append([item[0], str(item[1])])

    table = Table(data, colWidths=[10*cm, 5*cm])
    table.setStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT')
    ])

    elements.append(table)
    elements.append(Spacer(1, 25))

    elements.append(Paragraph(f"<b>Total Amount: ₹ {total}</b>", styles['Normal']))
    elements.append(Paragraph(f"<b>Paid Amount: ₹ {paid}</b>", styles['Normal']))
    elements.append(Paragraph(f"<b>Balance Amount: ₹ {balance}</b>", styles['Normal']))

    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<b>Authorized Signature</b>", styles['Normal']))

    doc.build(
        elements,
        onFirstPage=lambda c, d: (watermark(c, d), add_page_number(c, d)),
        onLaterPages=lambda c, d: (watermark(c, d), add_page_number(c, d))
    )
    conn.close()

# -------- DAY REPORT PDF --------
def export_day_pdf(report, selected_date):
    folder = "D:/Hospital Day Report"
    os.makedirs(folder, exist_ok=True)

    safe_date = selected_date.replace("/", "-")
    pdf_path = f"{folder}/Day_Report_{safe_date}.pdf"
    chart_path = f"{folder}/chart_{safe_date}.png"

    labels = ['Completed', 'Pending', 'Cancelled']
    values = [report['appointments_completed'], report['appointments_pending'], report['appointments_cancelled']]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['green', 'orange', 'red'])
    plt.title("Appointment Status")
    plt.savefig(chart_path)
    plt.close()

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    try:
        logo_img = RLImage(LOGO_PATH, 4*cm, 4*cm)
    except:
        logo_img = Paragraph("", styles['Normal'])

    hospital_name = Paragraph("<b><font size=30 color=#003366>Naveen Care Hospital</font></b>", styles['Title'])
    address = Paragraph("<font size=15>45, Perumalpatti, East Street, Srivilliputtur<br/><br/>Phone: 9876543210</font>", styles['Normal'])

    header = Table([[logo_img, hospital_name], ['', address]], colWidths=[4*cm, 12*cm])
    header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(header)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b><font size=14>Date: {selected_date}</font></b>", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b><font size=22>DAY REPORT</font></b>", styles['Title']))
    elements.append(Spacer(1, 20))

    lines = [
        f"Patients Added: {report['patients_added']}",
        f"Doctors Added: {report['doctors_added']}",
        f"Total Appointments: {report['appointments_total']}",
        f"Completed: {report['appointments_completed']}",
        f"Pending: {report['appointments_pending']}",
        f"Cancelled: {report['appointments_cancelled']}",
        f"Total Bill: ₹ {report['total_bill']}",
        f"Paid Bill: ₹ {report['paid_bill']}",
        f"Balance Bill: ₹ {report['balance_bill']}",
    ]

    for line in lines:
        elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Appointment Chart</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    elements.append(RLImage(chart_path, 14*cm, 8*cm))

    doc.build(elements, onFirstPage=lambda c, d: (watermark(c, d), add_page_number(c, d)))
    messagebox.showinfo("Success", f"Day Report PDF exported successfully!\n\nSaved to:\n{pdf_path}")

# -------- WEEK REPORT PDF --------
def export_week_pdf(report, from_date, to_date, dates, patients, amounts):
    folder = "D:/Hospital Week Report"
    os.makedirs(folder, exist_ok=True)

    safe_from = from_date.replace("/", "-")
    safe_to = to_date.replace("/", "-")
    pdf_path = f"{folder}/Week_Report_{safe_from}_to_{safe_to}.pdf"
    chart_path = f"{folder}/chart_{safe_from}_to_{safe_to}.png"

    labels = ['Completed', 'Pending', 'Cancelled']
    values = [report['appointments_completed'], report['appointments_pending'], report['appointments_cancelled']]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['green', 'orange', 'red'])
    plt.title("Appointment Status")
    plt.savefig(chart_path)
    plt.close()

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    try:
        logo_img = RLImage(LOGO_PATH, 4*cm, 4*cm)
    except:
        logo_img = Paragraph("", styles['Normal'])

    hospital_name = Paragraph("<b><font size=30 color=#003366>Naveen Care Hospital</font></b>", styles['Title'])
    address = Paragraph("<font size=15>45, Perumalpatti, East Street, Srivilliputtur<br/><br/>Phone: 9876543210</font>", styles['Normal'])

    header = Table([[logo_img, hospital_name], ['', address]], colWidths=[4*cm, 12*cm])
    header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(header)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b><font size=14>From: {from_date}   To: {to_date}</font></b>", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b><font size=22>WEEK REPORT</font></b>", styles['Title']))
    elements.append(Spacer(1, 20))

    lines = [
        f"Total Patients Added: {report.get('total_patients', 0)}",
        f"Total Doctors Added: {report.get('total_doctors', 0)}",
        f"Total Appointments: {report.get('appointments_total', 0)}",
        f"Completed: {report.get('appointments_completed', 0)}",
        f"Pending: {report.get('appointments_pending', 0)}",
        f"Cancelled: {report.get('appointments_cancelled', 0)}",
        f"Total Amount: ₹ {report.get('total_amount', 0)}",
        f"Paid Amount: ₹ {report.get('paid_amount', 0)}",
        f"Balance Amount: ₹ {report.get('balance_amount', 0)}",
    ]

    for line in lines:
        elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Appointment Chart</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    elements.append(RLImage(chart_path, 14*cm, 8*cm))

    doc.build(elements, onFirstPage=lambda c, d: (watermark(c, d), add_page_number(c, d)))
    messagebox.showinfo("Success", f"Week Report PDF exported!\n\nSaved to:\n{pdf_path}")