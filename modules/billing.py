from tkinter import *
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image, ImageTk
from database.db import get_connection
from utils.helpers import add_background_logo, smart_title
from utils.pdf_exporter import create_full_bill_pdf

total_amount = 0
selected_item = None


def open_billing_screen(root):
    bill = Toplevel(root)
    bill.title("Billing Section")
    bill.state('zoomed')  # Full Screen
    bill.config(bg="#f2f2f2")

    add_background_logo(bill, "assets/logo.png")

    Label(bill, text="BILLING SECTION", font=("Arial", 40, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=60)

    btn_frame = Frame(bill, bg="#f2f2f2")
    btn_frame.pack(pady=40)

    Button(btn_frame, text="Add Bill", font=("Arial", 18, "bold"), bg="green", fg="white", width=22, height=3,
           command=lambda: open_add_bill(root)).grid(row=0, column=0, padx=25)

    Button(btn_frame, text="Pending Bill", font=("Arial", 18, "bold"), bg="orange", fg="white", width=22, height=3,
           command=lambda: open_pending_bill(root)).grid(row=0, column=1, padx=25)

    Button(btn_frame, text="History", font=("Arial", 18, "bold"), bg="blue", fg="white", width=22, height=3,
           command=lambda: open_history_bill(root)).grid(row=0, column=2, padx=25)

    Button(bill, text="Close", font=("Arial", 16, "bold"), bg="red", fg="white", width=14, command=bill.destroy).pack(pady=40)


def open_add_bill(root):
    global total_amount, selected_item
    total_amount = 0
    selected_item = None

    add = Toplevel(root)
    add.title("Add Bill")
    add.state('zoomed')  # Full Screen
    add.config(bg="#f2f2f2")

    add_background_logo(add, "assets/logo.png")

    Label(add, text="ADD BILL", font=("Arial", 35, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=20)

    top_frame = Frame(add, bg="#f2f2f2")
    top_frame.pack(pady=15)

    Label(top_frame, text="Select Patient:", font=("Arial", 16), bg="#f2f2f2").grid(row=0, column=0, padx=10)
    patient_bill_combo = ttk.Combobox(top_frame, font=("Arial", 14), width=35)
    patient_bill_combo.grid(row=0, column=1, padx=10)

    def load_patients(event=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM patient")
        rows = cur.fetchall()
        conn.close()
        patient_bill_combo['values'] = [f"{r[1]} - {r[0]}" for r in rows]

    patient_bill_combo.bind("<Button-1>", load_patients)

    item_frame = Frame(add, bg="#f2f2f2")
    item_frame.pack(pady=15)

    Label(item_frame, text="Item Name:", font=("Arial", 14), bg="#f2f2f2").grid(row=0, column=0, padx=5)
    item_entry = Entry(item_frame, font=("Arial", 14), width=22)
    item_entry.grid(row=0, column=1, padx=5)

    Label(item_frame, text="Amount:", font=("Arial", 14), bg="#f2f2f2").grid(row=0, column=2, padx=5)
    amount_entry = Entry(item_frame, font=("Arial", 14), width=12)
    amount_entry.grid(row=0, column=3, padx=5)

    def add_item():
        global total_amount
        item = smart_title(item_entry.get().strip())
        amount = amount_entry.get().strip()

        if item == "" or amount == "" or not amount.isdigit():
            messagebox.showerror("Error", "Enter valid item name and numeric amount")
            return

        amt = float(amount)
        bill_table.insert("", END, values=(item, amt))
        total_amount += amt
        total_label.config(text=f"Total Amount: ₹ {total_amount}")
        item_entry.delete(0, END)
        amount_entry.delete(0, END)

    Button(item_frame, text="Add Item", font=("Arial", 12, "bold"), bg="green", fg="white", command=add_item).grid(row=0, column=4, padx=10)

    table_frame = Frame(add, bg="#f2f2f2")
    table_frame.pack(pady=15)

    bill_table = ttk.Treeview(table_frame, columns=("Item", "Amount"), show="headings", height=10)
    bill_table.heading("Item", text="Item Name")
    bill_table.heading("Amount", text="Amount (₹)")
    bill_table.column("Item", width=400)
    bill_table.column("Amount", width=180)
    bill_table.pack()

    total_label = Label(add, text="Total Amount: ₹ 0", font=("Arial", 18, "bold"), bg="#f2f2f2", fg="red")
    total_label.pack(pady=10)

    pay_frame = Frame(add, bg="#f2f2f2")
    pay_frame.pack(pady=10)

    Label(pay_frame, text="Paying Amount (₹):", font=("Arial", 14), bg="#f2f2f2").grid(row=0, column=0, padx=5)
    pay_entry = Entry(pay_frame, font=("Arial", 14), width=18)
    pay_entry.grid(row=0, column=1, padx=5)

    def process_payment(is_pending=False):
        global total_amount
        if not patient_bill_combo.get().strip():
            messagebox.showerror("Error", "Select Patient")
            return
        if len(bill_table.get_children()) == 0:
            messagebox.showerror("Error", "Add at least one item")
            return

        pid = patient_bill_combo.get().strip().split(" - ")[-1]
        today = datetime.now().strftime("%d/%m/%Y")

        if is_pending:
            paid = 0.0
        else:
            pay_str = pay_entry.get().strip()
            if not pay_str or not pay_str.replace('.', '', 1).isdigit():
                messagebox.showerror("Error", "Enter valid Paying Amount")
                return
            paid = float(pay_str)

        if paid > total_amount:
            messagebox.showerror("Error", "Paying amount exceeds total bill!")
            return

        balance = total_amount - paid
        status = "PAID" if balance == 0 else "PENDING"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bill (patient_id, total, paid, balance, status, date_added)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pid, total_amount, paid, balance, status, today))
        bill_id = cur.lastrowid

        for child in bill_table.get_children():
            item, amt = bill_table.item(child, "values")
            cur.execute("""
                INSERT INTO bill_items (bill_id, item_name, amount)
                VALUES (?, ?, ?)
            """, (bill_id, item, float(amt)))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Bill Processed Successfully!")
        add.destroy()

    btn_frame = Frame(add, bg="#f2f2f2")
    btn_frame.pack(pady=20)

    Button(btn_frame, text="Move to Pending", font=("Arial", 14, "bold"), bg="orange", fg="white", width=16, command=lambda: process_payment(is_pending=True)).grid(row=0, column=0, padx=15)
    Button(btn_frame, text="Save & Paid", font=("Arial", 14, "bold"), bg="green", fg="white", width=16, command=lambda: process_payment(is_pending=False)).grid(row=0, column=1, padx=15)
    Button(btn_frame, text="Close", font=("Arial", 14, "bold"), bg="red", fg="white", width=14, command=add.destroy).grid(row=0, column=2, padx=15)


def open_pending_bill(root):
    pen = Toplevel(root)
    pen.title("Pending Bills")
    pen.state('zoomed')  # Full Screen
    pen.config(bg="#f2f2f2")

    Label(pen, text="PENDING BILLS", font=("Arial", 35, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=20)

    main = Frame(pen, bg="#f2f2f2")
    main.pack(fill=BOTH, expand=True, padx=30, pady=15)

    left = Frame(main, bg="#f2f2f2")
    left.pack(side=LEFT, fill=Y)

    pending_table = ttk.Treeview(left, columns=("BillID", "Patient", "Balance", "Status"), show="headings", height=20)
    pending_table.heading("BillID", text="Bill ID")
    pending_table.heading("Patient", text="Patient Info")
    pending_table.heading("Balance", text="Balance (₹)")
    pending_table.heading("Status", text="Status")
    pending_table.column("BillID", width=80)
    pending_table.column("Patient", width=250)
    pending_table.column("Balance", width=120)
    pending_table.column("Status", width=100)
    pending_table.pack()

    def load_pending():
        for r in pending_table.get_children():
            pending_table.delete(r)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, p.name || ' - ' || p.id, b.balance, b.status
            FROM bill b
            JOIN patient p ON b.patient_id = p.id
            WHERE b.status = 'PENDING'
        """)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            pending_table.insert("", END, values=r)

    load_pending()

    right = Frame(main, bg="#f2f2f2", bd=2, relief=RIDGE)
    right.pack(side=RIGHT, fill=BOTH, expand=True, padx=30)

    info_lbl = Label(right, text="Select a pending bill to settle", font=("Arial", 16), bg="#f2f2f2")
    info_lbl.pack(pady=30)

    pay_frame = Frame(right, bg="#f2f2f2")
    pay_frame.pack(pady=15)
    Label(pay_frame, text="Paying Amount (₹):", font=("Arial", 14), bg="#f2f2f2").pack(side=LEFT, padx=5)
    pay_entry = Entry(pay_frame, font=("Arial", 14), width=18)
    pay_entry.pack(side=LEFT, padx=5)

    def settle_bill():
        selected = pending_table.focus()
        if not selected:
            messagebox.showerror("Error", "Select a bill")
            return

        bill_id = pending_table.item(selected, "values")[0]
        pay_text = pay_entry.get().strip()

        if not pay_text or not pay_text.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Enter valid amount")
            return

        pay_amount = float(pay_text)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT balance, paid FROM bill WHERE id=?", (bill_id,))
        balance, already_paid = cur.fetchone()

        if pay_amount > balance:
            conn.close()
            messagebox.showerror("Error", "Paying amount exceeds balance!")
            return

        new_paid = already_paid + pay_amount
        new_balance = balance - pay_amount
        status = "PAID" if new_balance == 0 else "PENDING"

        cur.execute("UPDATE bill SET paid=?, balance=?, status=? WHERE id=?", (new_paid, new_balance, status, bill_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Payment Updated Successfully!")
        pay_entry.delete(0, END)
        load_pending()

    Button(right, text="Settle Payment", font=("Arial", 14, "bold"), bg="green", fg="white", width=16, command=settle_bill).pack(pady=30)


def open_history_bill(root):
    his = Toplevel(root)
    his.title("Bill History")
    his.state('zoomed')  # Full Screen
    his.config(bg="#f2f2f2")

    Label(his, text="BILL HISTORY", font=("Arial", 35, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=20)

    table_frame = Frame(his)
    table_frame.pack(fill=BOTH, expand=True, padx=30, pady=15)

    history_table = ttk.Treeview(table_frame, columns=("BillID", "Patient", "Paid", "Balance", "Status"), show="headings", height=18)
    history_table.heading("BillID", text="Bill ID")
    history_table.heading("Patient", text="Patient Name & ID")
    history_table.heading("Paid", text="Paid (₹)")
    history_table.heading("Balance", text="Balance (₹)")
    history_table.heading("Status", text="Status")

    for col in ("BillID", "Patient", "Paid", "Balance", "Status"):
        history_table.column(col, width=180)

    history_table.pack(fill=BOTH, expand=True)

    def load_history():
        for r in history_table.get_children():
            history_table.delete(r)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, p.name || ' - ' || p.id, b.paid, b.balance, b.status
            FROM bill b
            JOIN patient p ON b.patient_id = p.id
        """)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            history_table.insert("", END, values=r)

    load_history()

    def print_bill():
        selected = history_table.focus()
        if not selected:
            messagebox.showerror("Error", "Select a bill to print")
            return

        bill_id = history_table.item(selected, "values")[0]
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"Bill_{bill_id}_{now}.pdf"

        try:
            create_full_bill_pdf(path, bill_id)
            messagebox.showinfo("Success", f"Bill PDF Generated:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"PDF Export Failed: {e}")

    def delete_bill():
        selected = history_table.focus()
        if not selected:
            messagebox.showerror("Error", "Select a bill to delete")
            return

        bill_id = history_table.item(selected, "values")[0]
        if messagebox.askyesno("Confirm", f"Delete Bill ID {bill_id}?"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM bill WHERE id=?", (bill_id,))
            cur.execute("DELETE FROM bill_items WHERE bill_id=?", (bill_id,))
            conn.commit()
            conn.close()

            history_table.delete(selected)
            messagebox.showinfo("Deleted", "Bill deleted successfully")

    btn_frame = Frame(his, bg="#f2f2f2")
    btn_frame.pack(pady=20)

    Button(btn_frame, text="Print PDF", font=("Arial", 14, "bold"), bg="blue", fg="white", width=14, command=print_bill).pack(side=LEFT, padx=15)
    Button(btn_frame, text="Delete Bill", font=("Arial", 14, "bold"), bg="red", fg="white", width=14, command=delete_bill).pack(side=LEFT, padx=15)
    Button(btn_frame, text="Close", font=("Arial", 14, "bold"), bg="gray", fg="white", width=14, command=his.destroy).pack(side=LEFT, padx=15)