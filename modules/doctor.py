from tkinter import *
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
from PIL import Image, ImageTk
from database.db import get_connection
from utils.helpers import add_background_logo, capitalize_words

doctor_name_var = None
doctor_dept_var = None
doctor_mobile_var = None
doctor_gender_var = None
doctor_exp_var = None
doctor_exp_type_var = None
doctor_image_path = None
doctor_status_var = None
doctor_login_var = None
img_label_doc = None


def init_doctor_vars(root):
    global doctor_name_var, doctor_dept_var, doctor_mobile_var, doctor_gender_var
    global doctor_exp_var, doctor_exp_type_var, doctor_image_path, doctor_status_var, doctor_login_var

    doctor_name_var = StringVar(master=root)
    doctor_dept_var = StringVar(master=root)
    doctor_mobile_var = StringVar(master=root)
    doctor_gender_var = StringVar(master=root, value=" ")
    doctor_exp_var = StringVar(master=root)
    doctor_exp_type_var = StringVar(master=root, value="Years")
    doctor_image_path = StringVar(master=root)
    doctor_status_var = StringVar(master=root, value=" ")
    doctor_login_var = StringVar(master=root, value=" ")


def save_doctor():
    global img_label_doc
    if (doctor_name_var.get() == "" or doctor_dept_var.get() == "" or 
        doctor_mobile_var.get() == "" or doctor_exp_var.get() == ""):
        messagebox.showerror("Error", "Please fill all required fields")
        return

    if not doctor_mobile_var.get().isdigit() or len(doctor_mobile_var.get()) != 10:
        messagebox.showerror("Error", "Invalid Mobile Number")
        return

    if not doctor_exp_var.get().isdigit() or int(doctor_exp_var.get()) <= 0:
        messagebox.showerror("Error", "Please enter a valid Experience year")
        return

    today = datetime.now().strftime("%d/%m/%Y")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO doctor
        (name, department, mobile, gender, experience, image, status, login_status, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doctor_name_var.get().strip(),
        doctor_dept_var.get().strip(),
        doctor_mobile_var.get().strip(),
        doctor_gender_var.get(),
        doctor_exp_var.get() + " " + doctor_exp_type_var.get(),
        doctor_image_path.get(),
        doctor_status_var.get(),
        doctor_login_var.get(),
        today
    ))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Doctor Added Successfully")

    doctor_name_var.set("")
    doctor_dept_var.set("")
    doctor_mobile_var.set("")
    doctor_gender_var.set(" ")
    doctor_exp_var.set("")
    doctor_exp_type_var.set("Years")
    doctor_image_path.set("")
    doctor_login_var.set(" ")
    doctor_status_var.set(" ")

    if img_label_doc:
        img_label_doc.config(image="")
        img_label_doc.image = None


def open_doctor_screen(root):
    init_doctor_vars(root)
    doctor = Toplevel(root)
    doctor.title("Doctor Management")
    doctor.state('zoomed')  # Full Screen
    doctor.config(bg="#f2f2f2")

    add_background_logo(doctor, "assets/logo.png")

    Label(doctor, text="Doctor Management", font=("Arial", 40, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=30)

    main_frame = Frame(doctor, bg="#f2f2f2")
    main_frame.pack(pady=20)

    def toggle_status():
        if doctor_login_var.get() == "Offline":
            status_available.config(state=DISABLED)
            status_busy.config(state=DISABLED)
            doctor_status_var.set(" ")
        else:
            status_available.config(state=NORMAL)
            status_busy.config(state=NORMAL)
            doctor_status_var.set("Available")

    form = Frame(main_frame, bg="#f2f2f2")
    form.grid(row=0, column=0, padx=40)

    Label(form, text="Doctor Name", font=("Arial", 18), bg="#f2f2f2").grid(row=0, column=0, sticky=W, pady=8)
    name_entry = Entry(form, font=("Arial", 16), width=25, textvariable=doctor_name_var)
    name_entry.grid(row=0, column=1, pady=8)
    name_entry.bind("<FocusOut>", capitalize_words)

    Label(form, text="Department", font=("Arial", 18), bg="#f2f2f2").grid(row=1, column=0, sticky=W, pady=8)
    dept_entry = Entry(form, font=("Arial", 16), width=25, textvariable=doctor_dept_var)
    dept_entry.grid(row=1, column=1, pady=8)
    dept_entry.bind("<FocusOut>", capitalize_words)

    Label(form, text="Mobile", font=("Arial", 18), bg="#f2f2f2").grid(row=2, column=0, sticky=W, pady=8)
    Entry(form, font=("Arial", 16), width=25, textvariable=doctor_mobile_var).grid(row=2, column=1, pady=8)

    Label(form, text="Experience", font=("Arial", 18), bg="#f2f2f2").grid(row=3, column=0, sticky=W, pady=8)
    exp_frame = Frame(form, bg="#f2f2f2")
    exp_frame.grid(row=3, column=1, pady=8, sticky=W)

    Entry(exp_frame, textvariable=doctor_exp_var, font=("Arial", 16), width=12).pack(side=LEFT, padx=5)
    ttk.Combobox(exp_frame, textvariable=doctor_exp_type_var, values=["Years", "Months"], state="readonly", width=8, font=("Arial", 12)).pack(side=LEFT)

    Label(form, text="Gender", font=("Arial", 18), bg="#f2f2f2").grid(row=4, column=0, sticky=W, pady=8)
    gender_frame = Frame(form, bg="#f2f2f2")
    gender_frame.grid(row=4, column=1, pady=8, sticky=W)
    for g in ["Male", "Female", "Other"]:
        Radiobutton(gender_frame, text=g, variable=doctor_gender_var, value=g, bg="#f2f2f2", font=("Arial", 14)).pack(side=LEFT)

    Label(form, text="Login Status", font=("Arial", 18), bg="#f2f2f2").grid(row=5, column=0, sticky=W, pady=8)
    login_frame = Frame(form, bg="#f2f2f2")
    login_frame.grid(row=5, column=1, pady=8, sticky=W)
    Radiobutton(login_frame, text="Online", variable=doctor_login_var, value="Online", command=toggle_status, bg="#f2f2f2", font=("Arial", 14)).pack(side=LEFT)
    Radiobutton(login_frame, text="Offline", variable=doctor_login_var, value="Offline", command=toggle_status, bg="#f2f2f2", font=("Arial", 14)).pack(side=LEFT)

    Label(form, text="Status", font=("Arial", 18), bg="#f2f2f2").grid(row=6, column=0, sticky=W, pady=8)
    status_frame = Frame(form, bg="#f2f2f2")
    status_frame.grid(row=6, column=1, pady=8, sticky=W)
    status_available = Radiobutton(status_frame, text="Available", variable=doctor_status_var, value="Available", bg="#f2f2f2", font=("Arial", 14))
    status_available.pack(side=LEFT)
    status_busy = Radiobutton(status_frame, text="Busy", variable=doctor_status_var, value="Busy", bg="#f2f2f2", font=("Arial", 14))
    status_busy.pack(side=LEFT)

    img_frame = Frame(main_frame, bg="#f2f2f2")
    img_frame.grid(row=0, column=1, padx=40)

    Label(img_frame, text="Doctor Photo", font=("Arial", 18), bg="#f2f2f2").pack(pady=10)

    global img_label_doc
    img_label_doc = Label(img_frame, bg="#f2f2f2")
    img_label_doc.pack(pady=10)

    def upload_doctor_image():
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            doctor_image_path.set(path)
            img = Image.open(path).resize((200, 200))
            photo = ImageTk.PhotoImage(img)
            img_label_doc.config(image=photo)
            img_label_doc.image = photo

    Button(img_frame, text="Upload Image", bg="#003366", fg="white", font=("Arial", 14), command=upload_doctor_image).pack(pady=10)

    btn_frame = Frame(doctor, bg="#f2f2f2")
    btn_frame.pack(pady=30)

    Button(btn_frame, text="SAVE", bg="green", fg="white", font=("Arial", 16, "bold"), width=14, command=save_doctor).pack(side=LEFT, padx=15)
    Button(btn_frame, text="VIEW DOCTOR LIST", font=("Arial", 16, "bold"), bg="#003366", fg="white", width=20, command=lambda: open_view_doctor_screen(root)).pack(side=LEFT, padx=15)
    Button(btn_frame, text="CLOSE", bg="red", fg="white", font=("Arial", 16, "bold"), width=14, command=doctor.destroy).pack(side=LEFT, padx=15)


def open_view_doctor_screen(root):
    view = Toplevel(root)
    view.title("Doctor List")
    view.state('zoomed')  # Full Screen
    view.config(bg="#f2f2f2")

    Label(view, text="Doctor List", font=("Arial", 35, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=20)

    search_frame = Frame(view, bg="#f2f2f2")
    search_frame.pack(pady=10, padx=30, anchor=W)

    Label(search_frame, text="Search Doctor:", font=("Arial", 16), bg="#f2f2f2").pack(side=LEFT, padx=5)
    search_var = StringVar()
    search_entry = Entry(search_frame, textvariable=search_var, font=("Arial", 14))
    search_entry.pack(side=LEFT, padx=5)

    main_frame = Frame(view, bg="#f2f2f2")
    main_frame.pack(fill=BOTH, expand=True, padx=30, pady=10)

    table_frame = Frame(main_frame)
    table_frame.pack(side=LEFT, fill=BOTH, expand=True)

    scroll_y = Scrollbar(table_frame, orient=VERTICAL)
    scroll_y.pack(side=RIGHT, fill=Y)

    doctor_table = ttk.Treeview(
        table_frame,
        columns=("ID", "Name", "Dept", "Mobile", "Gender", "Exp", "Login", "Status"),
        yscrollcommand=scroll_y.set,
        show="headings",
        height=20
    )
    scroll_y.config(command=doctor_table.yview)

    for col in ("ID", "Name", "Dept", "Mobile", "Gender", "Exp", "Login", "Status"):
        doctor_table.heading(col, text=col)
        doctor_table.column(col, width=130)

    doctor_table.pack(fill=BOTH, expand=True)

    details = Frame(main_frame, bg="#f2f2f2", bd=2, relief=RIDGE)
    details.pack(side=RIGHT, fill=BOTH, padx=30)

    img_label_details = Label(details, bg="#f2f2f2")
    img_label_details.pack(pady=15)

    info = {}
    for f in ["ID", "Name", "Dept", "Mobile", "Gender", "Exp", "Login", "Status"]:
        lbl = Label(details, text=f"{f}: ", font=("Arial", 14), bg="#f2f2f2")
        lbl.pack(anchor=W, pady=4)
        info[f] = lbl

    def search_doctor(*args):
        query = search_var.get().strip().lower()
        for item in doctor_table.get_children():
            doctor_table.delete(item)

        conn = get_connection()
        cur = conn.cursor()
        if query == "":
            cur.execute("SELECT id, name, department, mobile, gender, experience, login_status, status FROM doctor")
        else:
            cur.execute("SELECT id, name, department, mobile, gender, experience, login_status, status FROM doctor WHERE LOWER(name) LIKE ?", ('%' + query + '%',))

        rows = cur.fetchall()
        for row in rows:
            doctor_table.insert("", END, values=row)
        conn.close()

    search_var.trace_add("write", search_doctor)
    search_doctor()

    def show_details(event):
        sel = doctor_table.focus()
        if not sel:
            return
        vals = doctor_table.item(sel, "values")
        doc_id = vals[0]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT image FROM doctor WHERE id=?", (doc_id,))
        row = cur.fetchone()
        conn.close()

        path = row[0] if row else ""
        try:
            img = Image.open(path).resize((180, 180))
            photo = ImageTk.PhotoImage(img)
            img_label_details.config(image=photo)
            img_label_details.image = photo
        except:
            img_label_details.config(image="", text="No Image")

        fields = ["ID", "Name", "Dept", "Mobile", "Gender", "Exp", "Login", "Status"]
        for i, f in enumerate(fields):
            info[f].config(text=f"{f}: {vals[i]}")

    doctor_table.bind("<ButtonRelease-1>", show_details)

    def delete_doctor():
        selected = doctor_table.focus()
        if not selected:
            messagebox.showerror("Error", "Select a doctor to delete")
            return
        doc_id = doctor_table.item(selected, "values")[0]
        if messagebox.askyesno("Confirm", f"Delete Doctor ID {doc_id}?"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM doctor WHERE id=?", (doc_id,))
            conn.commit()
            conn.close()
            doctor_table.delete(selected)
            messagebox.showinfo("Deleted", "Doctor deleted successfully")

    btn_frame = Frame(view, bg="#f2f2f2")
    btn_frame.pack(pady=20)

    Button(btn_frame, text="DELETE", bg="red", fg="white", font=("Arial", 14, "bold"), width=14, command=delete_doctor).pack(side=LEFT, padx=10)
    Button(btn_frame, text="CLOSE", bg="gray", fg="white", font=("Arial", 14, "bold"), width=14, command=view.destroy).pack(side=LEFT, padx=10)