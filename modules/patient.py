from tkinter import *
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
from PIL import Image, ImageTk
from database.db import get_connection
from utils.helpers import add_background_logo, capitalize_words

name_var = None
age_var = None
mobile_var = None
disease_var = None
gender_var = None
image_path = None
img_label = None


def init_patient_vars(root):
    global name_var, age_var, mobile_var, disease_var, gender_var, image_path
    name_var = StringVar(master=root)
    age_var = StringVar(master=root)
    mobile_var = StringVar(master=root)
    disease_var = StringVar(master=root)
    gender_var = StringVar(master=root, value=" ")
    image_path = StringVar(master=root)


def save_patient():
    global img_label
    age = age_var.get().strip()
    mobile = mobile_var.get().strip()

    if (name_var.get() == "" or age == "" or mobile == "" or 
        gender_var.get().strip() == "" or disease_var.get() == ""):
        messagebox.showerror("Error", "Please fill all required fields")
        return

    if not age.isdigit() or int(age) <= 0:
        messagebox.showerror("Error", "Please enter a valid Age")
        return

    if not mobile.isdigit() or len(mobile) != 10:
        messagebox.showerror("Error", "Please enter a valid 10-digit Mobile Number")
        return

    today = datetime.now().strftime("%d/%m/%Y")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patient (name, age, mobile, gender, disease, image, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name_var.get().strip(), age, mobile, gender_var.get(), disease_var.get().strip(), image_path.get(), today))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Patient Added Successfully")

    name_var.set("")
    age_var.set("")
    mobile_var.set("")
    disease_var.set("")
    gender_var.set(" ")
    image_path.set("")

    if img_label:
        img_label.config(image="")
        img_label.image = None


def open_patient_screen(root):
    init_patient_vars(root)
    patient = Toplevel(root)
    patient.title("Patient Management")
    patient.state('zoomed')  # Full Screen
    patient.config(bg="#f2f2f2")

    add_background_logo(patient, "assets/logo.png")

    Label(patient, text="Patient Management", font=("Arial", 40, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=30)

    main_frame = Frame(patient, bg="#f2f2f2")
    main_frame.pack(pady=20)

    form = Frame(main_frame, bg="#f2f2f2")
    form.grid(row=0, column=0, padx=40)

    Label(form, text="Patient Name", font=("Arial", 18), bg="#f2f2f2").grid(row=0, column=0, sticky=W, pady=8)
    name_entry = Entry(form, font=("Arial", 16), width=25, textvariable=name_var)
    name_entry.grid(row=0, column=1, pady=8)
    name_entry.bind("<FocusOut>", capitalize_words)

    Label(form, text="Age", font=("Arial", 18), bg="#f2f2f2").grid(row=1, column=0, sticky=W, pady=8)
    Entry(form, font=("Arial", 16), width=25, textvariable=age_var).grid(row=1, column=1, pady=8)

    Label(form, text="Mobile Number", font=("Arial", 18), bg="#f2f2f2").grid(row=2, column=0, sticky=W, pady=8)
    Entry(form, font=("Arial", 16), width=25, textvariable=mobile_var).grid(row=2, column=1, pady=8)

    Label(form, text="Disease", font=("Arial", 18), bg="#f2f2f2").grid(row=3, column=0, sticky=W, pady=8)
    disease_entry = Entry(form, font=("Arial", 16), width=25, textvariable=disease_var)
    disease_entry.grid(row=3, column=1, pady=8)
    disease_entry.bind("<FocusOut>", capitalize_words)

    Label(form, text="Gender", font=("Arial", 18), bg="#f2f2f2").grid(row=4, column=0, sticky=W, pady=8)
    gender_frame = Frame(form, bg="#f2f2f2")
    gender_frame.grid(row=4, column=1, pady=8)

    for g in ["Male", "Female", "Other"]:
        Radiobutton(gender_frame, text=g, variable=gender_var, value=g, bg="#f2f2f2", font=("Arial", 14)).pack(side=LEFT)

    img_frame = Frame(main_frame, bg="#f2f2f2")
    img_frame.grid(row=0, column=1, padx=40)

    Label(img_frame, text="Patient Photo", font=("Arial", 18), bg="#f2f2f2").pack(pady=10)

    global img_label
    img_label = Label(img_frame, bg="#f2f2f2")
    img_label.pack(pady=10)

    def upload_image():
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            image_path.set(path)
            img = Image.open(path).resize((200, 200))
            photo = ImageTk.PhotoImage(img)
            img_label.config(image=photo)
            img_label.image = photo

    Button(img_frame, text="Upload Image", bg="#003366", fg="white", font=("Arial", 14), command=upload_image).pack(pady=10)

    btn_frame = Frame(patient, bg="#f2f2f2")
    btn_frame.pack(pady=30)

    Button(btn_frame, text="SAVE", font=("Arial", 16, "bold"), bg="green", fg="white", width=14, command=save_patient).pack(side=LEFT, padx=15)
    Button(btn_frame, text="VIEW PATIENT LIST", font=("Arial", 16, "bold"), bg="#003366", fg="white", width=20, command=lambda: open_view_patient_screen(root)).pack(side=LEFT, padx=15)
    Button(btn_frame, text="CLOSE", font=("Arial", 16, "bold"), bg="red", fg="white", width=14, command=patient.destroy).pack(side=LEFT, padx=15)


def open_view_patient_screen(root):
    view = Toplevel(root)
    view.title("View Patients")
    view.state('zoomed')  # Full Screen
    view.config(bg="#f2f2f2")

    Label(view, text="Patient List", font=("Arial", 35, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=20)

    search_frame = Frame(view, bg="#f2f2f2")
    search_frame.pack(pady=10, padx=30, anchor=W)

    Label(search_frame, text="Search Patient:", font=("Arial", 16), bg="#f2f2f2").pack(side=LEFT, padx=5)
    search_var = StringVar()
    search_entry = Entry(search_frame, textvariable=search_var, font=("Arial", 14))
    search_entry.pack(side=LEFT, padx=5)

    main_frame = Frame(view, bg="#f2f2f2")
    main_frame.pack(fill=BOTH, expand=True, padx=30, pady=10)

    table_frame = Frame(main_frame)
    table_frame.pack(side=LEFT, fill=BOTH, expand=True)

    scroll_y = Scrollbar(table_frame, orient=VERTICAL)
    scroll_y.pack(side=RIGHT, fill=Y)

    patient_table = ttk.Treeview(
        table_frame,
        columns=("ID", "Name", "Age", "Mobile", "Gender", "Disease"),
        yscrollcommand=scroll_y.set,
        show="headings",
        height=20
    )
    scroll_y.config(command=patient_table.yview)

    for col in ("ID", "Name", "Age", "Mobile", "Gender", "Disease"):
        patient_table.heading(col, text=col)
        patient_table.column(col, width=140)

    patient_table.pack(fill=BOTH, expand=True)

    details_frame = Frame(main_frame, bg="#f2f2f2", bd=2, relief=RIDGE)
    details_frame.pack(side=RIGHT, fill=BOTH, expand=False, padx=30)

    img_label_view = Label(details_frame, bg="#f2f2f2")
    img_label_view.pack(pady=15)

    info_labels = {}
    for field in ["ID", "Name", "Age", "Mobile", "Gender", "Disease"]:
        lbl = Label(details_frame, text=f"{field}: ", font=("Arial", 16), bg="#f2f2f2")
        lbl.pack(anchor=W, pady=5)
        info_labels[field] = lbl

    def search_patient(*args):
        query = search_var.get().strip().lower()
        for item in patient_table.get_children():
            patient_table.delete(item)

        conn = get_connection()
        cur = conn.cursor()
        if query == "":
            cur.execute("SELECT id, name, age, mobile, gender, disease FROM patient")
        else:
            cur.execute("SELECT id, name, age, mobile, gender, disease FROM patient WHERE LOWER(name) LIKE ?", ('%' + query + '%',))

        rows = cur.fetchall()
        for row in rows:
            patient_table.insert("", END, values=row[:6])
        conn.close()

    search_var.trace_add("write", search_patient)
    search_patient()

    def show_details(event):
        selected = patient_table.focus()
        if selected:
            values = patient_table.item(selected, "values")
            patient_id = values[0]

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT image FROM patient WHERE id=?", (patient_id,))
            row = cur.fetchone()
            conn.close()

            img_path = row[0] if row else ""
            try:
                img = Image.open(img_path).resize((200, 200))
                photo = ImageTk.PhotoImage(img)
                img_label_view.config(image=photo)
                img_label_view.image = photo
            except:
                img_label_view.config(image="", text="No Image")

            fields = ["ID", "Name", "Age", "Mobile", "Gender", "Disease"]
            for i, field in enumerate(fields):
                info_labels[field].config(text=f"{field}: {values[i]}")

    patient_table.bind("<ButtonRelease-1>", show_details)

    def delete_patient():
        selected = patient_table.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a patient to delete")
            return
        patient_id = patient_table.item(selected, "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Delete patient ID {patient_id}?"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM patient WHERE id=?", (patient_id,))
            conn.commit()
            conn.close()
            patient_table.delete(selected)
            messagebox.showinfo("Deleted", "Patient deleted successfully")

    btn_frame = Frame(view, bg="#f2f2f2")
    btn_frame.pack(pady=20)

    Button(btn_frame, text="DELETE", bg="red", fg="white", font=("Arial", 14, "bold"), width=14, command=delete_patient).pack(side=LEFT, padx=10)
    Button(btn_frame, text="CLOSE", bg="gray", fg="white", font=("Arial", 14, "bold"), width=14, command=view.destroy).pack(side=LEFT, padx=10)