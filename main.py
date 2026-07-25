from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from database.db import init_db
from utils.helpers import add_background_logo
from modules.patient import open_patient_screen
from modules.doctor import open_doctor_screen
from modules.appointment import open_appointment_screen
from modules.billing import open_billing_screen
from modules.reports import open_report_module

# Initialize SQLite Database & Tables
init_db()

root = Tk()
root.withdraw()


def maximize_win(win):
    """Auto Maximizes window to Laptop Full Screen"""
    win.state('zoomed')


def open_dashboard():
    dash = Toplevel(root)
    dash.title("Hospital Management System - Dashboard")
    maximize_win(dash)
    dash.config(bg="#f2f2f2")

    add_background_logo(dash, "assets/logo.png")

    top_frame = Frame(dash, bg="#f2f2f2")
    top_frame.pack(fill=X, pady=20)

    try:
        logo2 = ImageTk.PhotoImage(Image.open("assets/logo.png").resize((110, 110)))
        dash.logo2 = logo2
        Label(top_frame, image=logo2, bg="#f2f2f2").pack(side=TOP, padx=20)
    except Exception as e:
        print("Logo display error:", e)

    Label(top_frame, text="NAVEEN CARE HOSPITAL", font=("Arial", 45, "bold"), bg="#f2f2f2", fg="#003366").pack(side=TOP)

    # Asset Icons
    try:
        patient_img = ImageTk.PhotoImage(Image.open("assets/patient.png").resize((80, 80)))
        doctor_img = ImageTk.PhotoImage(Image.open("assets/doctor.png").resize((80, 80)))
        appoint_img = ImageTk.PhotoImage(Image.open("assets/appointment.png").resize((80, 80)))
        billing_img = ImageTk.PhotoImage(Image.open("assets/billing.png").resize((80, 80)))
        report_img = ImageTk.PhotoImage(Image.open("assets/report.png").resize((80, 80)))

        dash.patient_img = patient_img
        dash.doctor_img = doctor_img
        dash.appoint_img = appoint_img
        dash.billing_img = billing_img
        dash.report_img = report_img
    except Exception as e:
        print("Warning: Navigation icons missing in assets/", e)

    frame = Frame(dash, bg="#f2f2f2")
    frame.pack(pady=40)

    # Navigation Grid
    Button(frame, image=getattr(dash, 'patient_img', None), text="Patient", compound=TOP, font=("Arial", 16, "bold"), width=180, height=150, command=lambda: open_patient_screen(root)).grid(row=0, column=0, padx=25, pady=20)
    Button(frame, image=getattr(dash, 'doctor_img', None), text="Doctor", compound=TOP, font=("Arial", 16, "bold"), width=180, height=150, command=lambda: open_doctor_screen(root)).grid(row=0, column=1, padx=25, pady=20)
    Button(frame, image=getattr(dash, 'appoint_img', None), text="Appointment", compound=TOP, font=("Arial", 16, "bold"), width=180, height=150, command=lambda: open_appointment_screen(root)).grid(row=0, column=2, padx=25, pady=20)
    Button(frame, image=getattr(dash, 'billing_img', None), text="Billing", compound=TOP, font=("Arial", 16, "bold"), width=180, height=150, command=lambda: open_billing_screen(root)).grid(row=1, column=0, columnspan=2, padx=25, pady=20)
    Button(frame, image=getattr(dash, 'report_img', None), text="Reports", compound=TOP, font=("Arial", 16, "bold"), width=180, height=150, command=lambda: open_report_module(root)).grid(row=1, column=1, columnspan=2, padx=25, pady=20)

    btn_frame = Frame(dash, bg="#f2f2f2")
    btn_frame.pack(pady=30)

    Button(btn_frame, text="LOGOUT", bg="red", fg="white", font=("Arial", 14, "bold"), width=15, height=2, command=lambda: [dash.destroy(), open_login()]).grid(row=0, column=0, padx=20)
    Button(btn_frame, text="EXIT", bg="black", fg="white", font=("Arial", 14, "bold"), width=15, height=2, command=root.destroy).grid(row=0, column=1, padx=20)


def open_login():
    if 'splash' in globals() and splash.winfo_exists():
        splash.destroy()

    login = Toplevel(root)
    login.title("Login - Naveen Care Hospital")
    maximize_win(login)
    login.config(bg="#f2f2f2")
    add_background_logo(login, "assets/logo.png")

    Label(login, text="Hospital Login", font=("Arial", 45, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=60)

    Label(login, text="Username", bg="#f2f2f2", font=("Arial", 18)).pack()
    username_entry = Entry(login, font=("Arial", 16), width=25)
    username_entry.pack(pady=10)

    Label(login, text="Password", bg="#f2f2f2", font=("Arial", 18)).pack()
    password_entry = Entry(login, show="*", font=("Arial", 16), width=25)
    password_entry.pack(pady=10)

    def login_check():
        if username_entry.get() in ["admin", "kalai"] and password_entry.get() == "123":
            messagebox.showinfo("Login", f"Login Successful! Welcome {username_entry.get()}")
            login.destroy()
            open_dashboard()
        else:
            messagebox.showerror("Login", "Invalid Username or Password")

    Button(login, text="LOGIN", bg="green", fg="white", font=("Arial", 14, "bold"), width=14, height=2, command=login_check).pack(pady=20)
    Button(login, text="EXIT", bg="red", fg="white", font=("Arial", 14, "bold"), width=14, height=2, command=root.destroy).pack()


# Splash Screen
splash = Toplevel(root)
splash.title("Naveen Care Hospital")
maximize_win(splash)
splash.config(bg="#f2f2f2")
add_background_logo(splash, "assets/logo.png")

try:
    logo_img = ImageTk.PhotoImage(Image.open("assets/logo.png").resize((220, 220)))
    splash.logo_img = logo_img
    Label(splash, image=logo_img, bg="#f2f2f2").pack(pady=60)
except:
    pass

Label(splash, text="NAVEEN CARE HOSPITAL", font=("Arial", 50, "bold"), bg="#f2f2f2", fg="#003366").pack()

splash.after(2000, open_login)
splash.mainloop()