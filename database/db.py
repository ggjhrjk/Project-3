import sqlite3

DB_NAME = "hospital.db"

def get_connection():
    """Returns a fresh connection object to SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    """Initializes all required tables for Hospital Management System"""
    conn = get_connection()
    cur = conn.cursor()

    # 1. Patient Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patient (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        mobile TEXT,
        gender TEXT,
        disease TEXT,
        image TEXT,
        date_added TEXT
    )
    """)

    # 2. Doctor Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        mobile TEXT,
        gender TEXT,
        experience TEXT,
        image TEXT,
        status TEXT,
        login_status TEXT,
        date_added TEXT
    )
    """)

    # 3. Appointment Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT,
        from_time TEXT,
        to_time TEXT,
        notes TEXT,
        status TEXT,
        FOREIGN KEY(patient_id) REFERENCES patient(id),
        FOREIGN KEY(doctor_id) REFERENCES doctor(id)
    )
    """)

    # 4. Bill Master Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        total REAL,
        paid REAL,
        balance REAL,
        status TEXT,
        date_added TEXT
    )
    """)

    # 5. Bill Items Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        item_name TEXT,
        amount REAL,
        FOREIGN KEY(bill_id) REFERENCES bill(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database & Tables initialized successfully!")