# 🏥 Hospital Management System (Tkinter GUI)

A modular, professional Python Tkinter application for managing hospital workflow including Patient Records, Doctor Availability, Appointment Scheduling, Billing, and Analytics Reports with PDF Exports.

## ✨ Features
* 👤 **Patient Management**: Add, View, Search, and Delete Patients with Photo attachments.
* 🩺 **Doctor Management**: Availability status tracking, Online/Offline modes, Experience details.
* 📅 **Appointment System**: Dynamic 12hr/24hr time slot validation & Overlap protection.
* 🧾 **Billing & Accounts**: Dynamic items addition, Split Payments (Paid / Pending History).
* 📊 **Reports & Analytics**: Daily/Weekly summary reports powered by Matplotlib charts with PDF downloads.

## 🛠️ Tech Stack
* **Language**: Python 3
* **GUI Framework**: Tkinter
* **Database**: SQLite3
* **PDF Export**: ReportLab
* **Visualization**: Matplotlib

## 🚀 How to Run Locally
```bash
pip install pillow tkcalendar reportlab matplotlib
python main.py