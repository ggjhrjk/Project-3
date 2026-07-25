from tkinter import *
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image, ImageTk
from database.db import get_connection
from utils.helpers import add_background_logo

patient_combo = None
doctor_combo = None
dd_entry = None
mm_entry = None
yyyy_entry = None
from_hour = None
from_min = None
from_ampm = None
to_hour = None
to_min = None
to_ampm = None
notes_entry = None


def open_appointment_screen(root):
    appoint = Toplevel(root)
    appoint.title("Appointment Module")
    appoint.state('zoomed')  # Full Screen
    appoint.config(bg="#f2f2f2")

    add_background_logo(appoint, "assets/logo.png")

    Label(appoint, text="Appointment Module", font=("Arial", 40, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=60)

    btn_frame = Frame(appoint, bg="#f2f2f2")
    btn_frame.pack(pady=40)

    Button(btn_frame, text="Appointment Booking", font=("Arial", 18, "bold"), width=24, height=3, bg="green", fg="white",
           command=lambda: open_booking_screen(root)).grid(row=0, column=0, padx=30)

    Button(btn_frame, text="View Appointments", font=("Arial", 18, "bold"), width=24, height=3, bg="violet", fg="white",
           command=lambda: open_view_appointment(root)).grid(row=0, column=1, padx=30)

    Button(appoint, text="Close", font=("Arial", 16, "bold"), width=14, bg="red", fg="white", command=appoint.destroy).pack(pady=40)


def convert_to_24hr(date_str, time_str):
    dd, mm, yyyy = map(int, date_str.split("/"))
    hour, rest = time_str.split(":")
    minute, ampm = rest.split()

    hour = int(hour)
    minute = int(minute)

    if ampm == "PM" and hour != 12:
        hour += 12
    if ampm == "AM" and hour == 12:
        hour = 0

    return datetime(yyyy, mm, dd, hour, minute)


def is_doctor_available(doctor_id, date, new_from, new_to):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT from_time, to_time FROM appointment WHERE doctor_id=? AND date=? AND status != 'Cancelled'", (doctor_id, date))
    rows = cur.fetchall()
    conn.close()

    new_from_dt = convert_to_24hr(date, new_from)
    new_to_dt = convert_to_24hr(date, new_to)

    for row in rows:
        old_from, old_to = row
        try:
            old_from_dt = convert_to_24hr(date, old_from)
            old_to_dt = convert_to_24hr(date, old_to)

            if new_from_dt < old_to_dt and new_to_dt > old_from_dt:
                return False
        except Exception as e:
            print("Time error:", e)

    return True


def open_booking_screen(root):
    global patient_combo, doctor_combo, dd_entry, mm_entry, yyyy_entry
    global from_hour, from_min, from_ampm, to_hour, to_min, to_ampm, notes_entry

    book = Toplevel(root)
    book.title("Book Appointment")
    book.state('zoomed')  # Full Screen
    book.config(bg="#f2f2f2")

    add_background_logo(book, "assets/logo.png")

    Label(book, text="Appointment Booking", font=("Arial", 35, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=30)

    form = Frame(book, bg="#f2f2f2")
    form.pack(pady=20)

    Label(form, text="Select Patient:", font=("Arial", 16), bg="#f2f2f2").grid(row=0, column=0, padx=15, pady=12, sticky="w")
    patient_combo = ttk.Combobox(form, font=("Arial", 14), width=30)
    patient_combo.grid(row=0, column=1, padx=15, pady=12)

    def load_patients(event=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM patient")
        rows = cur.fetchall()
        conn.close()
        patient_combo['values'] = [f"{r[1]} - {r[0]}" for r in rows]

    patient_combo.bind("<Button-1>", load_patients)

    Label(form, text="Select Doctor:", font=("Arial", 16), bg="#f2f2f2").grid(row=1, column=0, padx=15, pady=12, sticky="w")
    doctor_combo = ttk.Combobox(form, font=("Arial", 14), width=30)
    doctor_combo.grid(row=1, column=1, padx=15, pady=12)

    def load_doctors(event=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM doctor WHERE login_status='Online' AND status='Available'")
        rows = cur.fetchall()
        conn.close()
        doctor_combo['values'] = [f"{r[1]} - {r[0]}" for r in rows]

    doctor_combo.bind("<Button-1>", load_doctors)

    Label(form, text="Date (DD/MM/YYYY):", font=("Arial", 16), bg="#f2f2f2").grid(row=2, column=0, padx=15, pady=12, sticky="w")
    date_frame = Frame(form, bg="#f2f2f2")
    date_frame.grid(row=2, column=1, padx=15, pady=12, sticky="w")

    dd_entry = Entry(date_frame, font=("Arial", 14), width=5, justify="center")
    dd_entry.pack(side=LEFT)
    Label(date_frame, text="/", font=("Arial", 16), bg="#f2f2f2").pack(side=LEFT)
    mm_entry = Entry(date_frame, font=("Arial", 14), width=5, justify="center")
    mm_entry.pack(side=LEFT)
    Label(date_frame, text="/", font=("Arial", 16), bg="#f2f2f2").pack(side=LEFT)
    yyyy_entry = Entry(date_frame, font=("Arial", 14), width=8, justify="center")
    yyyy_entry.pack(side=LEFT)

    Label(form, text="From Time:", font=("Arial", 16), bg="#f2f2f2").grid(row=3, column=0, padx=15, pady=12, sticky="w")
    from_frame = Frame(form, bg="#f2f2f2")
    from_frame.grid(row=3, column=1, padx=15, pady=12, sticky="w")
    from_hour = Entry(from_frame, font=("Arial", 14), width=5, justify="center")
    from_hour.pack(side=LEFT)
    Label(from_frame, text=":", font=("Arial", 16), bg="#f2f2f2").pack(side=LEFT)
    from_min = Entry(from_frame, font=("Arial", 14), width=5, justify="center")
    from_min.pack(side=LEFT)
    from_ampm = ttk.Combobox(from_frame, values=["AM", "PM"], font=("Arial", 13), width=6, state="readonly")
    from_ampm.pack(side=LEFT, padx=5)
    from_ampm.set("AM")

    Label(form, text="To Time:", font=("Arial", 16), bg="#f2f2f2").grid(row=4, column=0, padx=15, pady=12, sticky="w")
    to_frame = Frame(form, bg="#f2f2f2")
    to_frame.grid(row=4, column=1, padx=15, pady=12, sticky="w")
    to_hour = Entry(to_frame, font=("Arial", 14), width=5, justify="center")
    to_hour.pack(side=LEFT)
    Label(to_frame, text=":", font=("Arial", 16), bg="#f2f2f2").pack(side=LEFT)
    to_min = Entry(to_frame, font=("Arial", 14), width=5, justify="center")
    to_min.pack(side=LEFT)
    to_ampm = ttk.Combobox(to_frame, values=["AM", "PM"], font=("Arial", 13), width=6, state="readonly")
    to_ampm.pack(side=LEFT, padx=5)
    to_ampm.set("AM")

    Label(form, text="Notes (Optional):", font=("Arial", 16), bg="#f2f2f2").grid(row=5, column=0, padx=15, pady=12, sticky="w")
    notes_entry = Entry(form, font=("Arial", 14), width=32)
    notes_entry.grid(row=5, column=1, padx=15, pady=12)

    def save_appointment():
        patient_data = patient_combo.get().strip()
        doctor_data = doctor_combo.get().strip()
        dd, mm, yyyy = dd_entry.get().strip(), mm_entry.get().strip(), yyyy_entry.get().strip()
        fh, fm = from_hour.get().strip(), from_min.get().strip()
        th, tm = to_hour.get().strip(), to_min.get().strip()

        if not patient_data or not doctor_data or not dd or not mm or not yyyy or not fh or not fm or not th or not tm:
            messagebox.showerror("Error", "Please fill all required fields")
            return

        patient_id = patient_data.split(" - ")[-1]
        doctor_id = doctor_data.split(" - ")[-1]
        date = f"{dd}/{mm}/{yyyy}"
        from_time = f"{fh}:{fm} {from_ampm.get()}"
        to_time = f"{th}:{tm} {to_ampm.get()}"

        if not is_doctor_available(doctor_id, date, from_time, to_time):
            messagebox.showerror("Doctor Busy", "Doctor is already booked for this time slot!")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO appointment (patient_id, doctor_id, date, from_time, to_time, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, date, from_time, to_time, notes_entry.get().strip(), "Pending"))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Appointment Booked Successfully!")
        book.destroy()

    btn_frame = Frame(book, bg="#f2f2f2")
    btn_frame.pack(pady=30)
    Button(btn_frame, text="Book Appointment", font=("Arial", 16, "bold"), bg="green", fg="white", width=18, command=save_appointment).pack(side=LEFT, padx=15)
    Button(btn_frame, text="Close", font=("Arial", 16, "bold"), bg="red", fg="white", width=14, command=book.destroy).pack(side=LEFT, padx=15)


def open_view_appointment(root):
    view = Toplevel(root)
    view.title("View Appointments")
    view.state('zoomed')  # Full Screen
    view.config(bg="#f2f2f2")

    Label(view, text="Appointment List", font=("Arial", 35, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=20)

    table_frame = Frame(view)
    table_frame.pack(fill=BOTH, expand=True, padx=30, pady=10)

    scroll_y = Scrollbar(table_frame, orient=VERTICAL)
    scroll_y.pack(side=RIGHT, fill=Y)

    appoint_table = ttk.Treeview(
        table_frame,
        columns=("AppID", "Patient", "Doctor", "Date", "From", "To", "Notes", "Status"),
        yscrollcommand=scroll_y.set,
        show="headings",
        height=18
    )
    scroll_y.config(command=appoint_table.yview)

    for col in ("AppID", "Patient", "Doctor", "Date", "From", "To", "Notes", "Status"):
        appoint_table.heading(col, text=col)
        appoint_table.column(col, width=140)

    appoint_table.pack(fill=BOTH, expand=True)

    def load_appointments():
        for item in appoint_table.get_children():
            appoint_table.delete(item)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT appointment.id,
                   patient.name || ' - ' || patient.id,
                   doctor.name || ' - ' || doctor.id,
                   appointment.date,
                   appointment.from_time,
                   appointment.to_time,
                   appointment.notes,
                   appointment.status
            FROM appointment
            JOIN patient ON appointment.patient_id = patient.id
            JOIN doctor ON appointment.doctor_id = doctor.id
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            appoint_table.insert("", END, values=row)

    load_appointments()

    def cancel_appointment():
        selected = appoint_table.focus()
        if not selected:
            messagebox.showerror("Error", "Select an appointment to cancel")
            return
        vals = appoint_table.item(selected, "values")
        app_id, status = vals[0], vals[7]

        if status == "Cancelled":
            messagebox.showinfo("Info", "Already cancelled")
            return

        if messagebox.askyesno("Confirm", f"Cancel Appointment ID {app_id}?"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE appointment SET status='Cancelled' WHERE id=?", (app_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Appointment Cancelled!")
            load_appointments()

    btn_frame = Frame(view, bg="#f2f2f2")
    btn_frame.pack(pady=20)
    Button(btn_frame, text="Cancel Appointment", bg="orange", fg="white", font=("Arial", 14, "bold"), width=18, command=cancel_appointment).pack(side=LEFT, padx=15)
    Button(btn_frame, text="Close", bg="gray", fg="white", font=("Arial", 14, "bold"), width=14, command=view.destroy).pack(side=LEFT, padx=15)