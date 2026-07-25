from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db import get_connection
from utils.helpers import add_background_logo
from utils.pdf_exporter import export_day_pdf, export_week_pdf

plt.switch_backend('Agg')

def maximize_win(win):
    """Auto Maximizes window to Full Screen"""
    win.state('zoomed')

def open_report_module(root):
    report = Toplevel(root)
    report.title("Report Module")
    maximize_win(report)
    report.config(bg="#f2f2f2")

    add_background_logo(report, "assets/logo.png")

    Label(report, text="REPORT MODULE", font=("Arial", 40, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=50)

    btn_frame = Frame(report, bg="#f2f2f2")
    btn_frame.pack(pady=40)

    Button(btn_frame, text="Day Report", font=("Arial", 18, "bold"), width=16, height=2, bg="green", fg="white",
           command=lambda: open_day_report(root)).grid(row=0, column=0, padx=20)

    Button(btn_frame, text="Week Report", font=("Arial", 18, "bold"), width=16, height=2, bg="orange", fg="white",
           command=lambda: open_week_report(root)).grid(row=0, column=1, padx=20)

    Button(btn_frame, text="Month Report", font=("Arial", 18, "bold"), width=16, height=2, bg="pink", fg="white",
           command=lambda: open_week_report(root)).grid(row=0, column=2, padx=20)

    Button(btn_frame, text="Year Report", font=("Arial", 18, "bold"), width=16, height=2, bg="purple", fg="white",
           command=lambda: open_week_report(root)).grid(row=0, column=3, padx=20)

    Button(report, text="Close", font=("Arial", 16, "bold"), width=14, height=2, bg="red", fg="white", command=report.destroy).pack(pady=40)

# ==================== DAY REPORT ====================
def generate_day_report(selected_date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM patient WHERE date_added=?", (selected_date,))
    total_patients = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM doctor WHERE date_added=?", (selected_date,))
    total_doctors = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT COUNT(*),
               SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END),
               SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END),
               SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END)
        FROM appointment WHERE date=?
    """, (selected_date,))
    row = cur.fetchone()

    cur.execute("SELECT SUM(total), SUM(paid), SUM(balance) FROM bill WHERE date_added=?", (selected_date,))
    b_row = cur.fetchone()
    conn.close()

    return {
        "patients_added": total_patients,
        "doctors_added": total_doctors,
        "appointments_total": row[0] or 0,
        "appointments_completed": row[1] or 0,
        "appointments_pending": row[2] or 0,
        "appointments_cancelled": row[3] or 0,
        "total_bill": b_row[0] or 0.0,
        "paid_bill": b_row[1] or 0.0,
        "balance_bill": b_row[2] or 0.0
    }

def draw_day_chart(parent, report_data):
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)
    labels = ["Completed", "Pending", "Cancelled"]
    values = [
        report_data["appointments_completed"],
        report_data["appointments_pending"],
        report_data["appointments_cancelled"]
    ]
    ax.bar(labels, values, color=['green', 'orange', 'red'])
    ax.set_title("Appointment Status Chart")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

def open_day_report_result(root, selected_date):
    report_data = generate_day_report(selected_date)

    result_win = Toplevel(root)
    result_win.title(f"Day Report - {selected_date}")
    maximize_win(result_win)
    result_win.config(bg="#f2f2f2")

    Label(result_win, text=f"Day Report: {selected_date}", font=("Arial", 28, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=10)

    # Scrollable Area to show all content + buttons properly
    canvas = Canvas(result_win, bg="#f2f2f2", highlightthickness=0)
    scrollbar = Scrollbar(result_win, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="#f2f2f2")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=20)
    scrollbar.pack(side="right", fill="y")

    # Data Display
    frame = Frame(scrollable_frame, bg="#f2f2f2")
    frame.pack(pady=10)

    for k, v in report_data.items():
        Label(frame, text=f"{k.replace('_', ' ').title()}: {v}", font=("Arial", 14, "bold"), bg="#f2f2f2").pack(anchor=W, pady=2)

    # Chart
    draw_day_chart(scrollable_frame, report_data)

    # Buttons Frame (Export PDF & Close)
    btn_frame = Frame(scrollable_frame, bg="#f2f2f2")
    btn_frame.pack(pady=20)

    Button(btn_frame, text="Export PDF", font=("Arial", 14, "bold"), bg="blue", fg="white", width=16, height=2,
           command=lambda: export_day_pdf(report_data, selected_date)).pack(side=LEFT, padx=15)
    Button(btn_frame, text="Close", font=("Arial", 14, "bold"), bg="red", fg="white", width=14, height=2,
           command=result_win.destroy).pack(side=LEFT, padx=15)

def open_day_report(root):
    day_win = Toplevel(root)
    day_win.title("Day Report")
    maximize_win(day_win)
    day_win.config(bg="#f2f2f2")

    add_background_logo(day_win, "assets/logo.png")

    Label(day_win, text="Select Date for Day Report", font=("Arial", 30, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=50)

    date_entry = DateEntry(day_win, width=15, font=("Arial", 18), date_pattern='dd/mm/yyyy')
    date_entry.pack(pady=30)

    Button(day_win, text="Generate Report", font=("Arial", 16, "bold"), bg="green", fg="white", width=16, height=2,
           command=lambda: open_day_report_result(root, date_entry.get())).pack(pady=20)
    Button(day_win, text="Close", font=("Arial", 14, "bold"), bg="red", fg="white", width=12,
           command=day_win.destroy).pack(pady=10)

# ==================== WEEK REPORT ====================
def generate_week_report(from_date, to_date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM patient WHERE date_added BETWEEN ? AND ?", (from_date, to_date))
    total_patients = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM doctor WHERE date_added BETWEEN ? AND ?", (from_date, to_date))
    total_doctors = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT COUNT(*),
               SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END),
               SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END),
               SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END)
        FROM appointment WHERE date BETWEEN ? AND ?
    """, (from_date, to_date))
    row = cur.fetchone()

    cur.execute("SELECT SUM(total), SUM(paid), SUM(balance) FROM bill WHERE date_added BETWEEN ? AND ?", (from_date, to_date))
    b_row = cur.fetchone()
    conn.close()

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "appointments_total": row[0] or 0,
        "appointments_completed": row[1] or 0,
        "appointments_pending": row[2] or 0,
        "appointments_cancelled": row[3] or 0,
        "total_amount": b_row[0] or 0.0,
        "paid_amount": b_row[1] or 0.0,
        "balance_amount": b_row[2] or 0.0
    }

def open_week_report_result(root, from_date, to_date):
    report_data = generate_week_report(from_date, to_date)

    result_win = Toplevel(root)
    result_win.title(f"Week Report - {from_date} to {to_date}")
    maximize_win(result_win)
    result_win.config(bg="#f2f2f2")

    Label(result_win, text=f"Week Report: {from_date} to {to_date}", font=("Arial", 28, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=10)

    canvas = Canvas(result_win, bg="#f2f2f2", highlightthickness=0)
    scrollbar = Scrollbar(result_win, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="#f2f2f2")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=20)
    scrollbar.pack(side="right", fill="y")

    frame = Frame(scrollable_frame, bg="#f2f2f2")
    frame.pack(pady=10)

    for k, v in report_data.items():
        Label(frame, text=f"{k.replace('_', ' ').title()}: {v}", font=("Arial", 14, "bold"), bg="#f2f2f2").pack(anchor=W, pady=2)

    draw_day_chart(scrollable_frame, {
        "appointments_completed": report_data["appointments_completed"],
        "appointments_pending": report_data["appointments_pending"],
        "appointments_cancelled": report_data["appointments_cancelled"]
    })

    btn_frame = Frame(scrollable_frame, bg="#f2f2f2")
    btn_frame.pack(pady=20)

    Button(btn_frame, text="Export PDF", font=("Arial", 14, "bold"), bg="blue", fg="white", width=16, height=2,
           command=lambda: export_week_pdf(report_data, from_date, to_date, [], [], [])).pack(side=LEFT, padx=15)
    Button(btn_frame, text="Close", font=("Arial", 14, "bold"), bg="red", fg="white", width=14, height=2,
           command=result_win.destroy).pack(side=LEFT, padx=15)

def open_week_report(root):
    week_win = Toplevel(root)
    week_win.title("Week Report")
    maximize_win(week_win)
    week_win.config(bg="#f2f2f2")

    add_background_logo(week_win, "assets/logo.png")

    Label(week_win, text="Select Date Range for Report", font=("Arial", 30, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=50)

    frame = Frame(week_win, bg="#f2f2f2")
    frame.pack(pady=20)

    Label(frame, text="From Date:", font=("Arial", 16, "bold"), bg="#f2f2f2").grid(row=0, column=0, padx=10)
    from_entry = DateEntry(frame, width=14, font=("Arial", 16), date_pattern='dd/mm/yyyy')
    from_entry.grid(row=0, column=1, padx=15)

    Label(frame, text="To Date:", font=("Arial", 16, "bold"), bg="#f2f2f2").grid(row=0, column=2, padx=10)
    to_entry = DateEntry(frame, width=14, font=("Arial", 16), date_pattern='dd/mm/yyyy')
    to_entry.grid(row=0, column=3, padx=15)

    Button(week_win, text="Generate Report", font=("Arial", 16, "bold"), bg="green", fg="white", width=16, height=2,
           command=lambda: open_week_report_result(root, from_entry.get(), to_entry.get())).pack(pady=30)
    Button(week_win, text="Close", font=("Arial", 14, "bold"), bg="red", fg="white", width=12,
           command=week_win.destroy).pack(pady=10)