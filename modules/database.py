import sqlite3
from datetime import datetime

DB_NAME = "payments.db"


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS payments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            message TEXT,

            amount INTEGER,

            name TEXT,

            whatsapp_datetime TEXT,

            status TEXT DEFAULT 'Pending',

            paid_amount INTEGER DEFAULT 0,

            paid_date TEXT,

            remarks TEXT,

            scanned_at TEXT

        )

    """)

    conn.commit()

    conn.close()


# =========================================================
# CHECK DUPLICATE
# =========================================================

def payment_exists(amount, name):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT id
        FROM payments
        WHERE amount = ?
        AND LOWER(name) = LOWER(?)

    """, (

        amount,
        name

    ))

    result = cursor.fetchone()

    conn.close()

    return result is not None


# =========================================================
# SAVE PAYMENT REQUEST
# =========================================================

def save_payment(data, whatsapp_datetime=""):

    amount = data["amount"]

    name = data["name"]

    if payment_exists(amount, name):

        print("DUPLICATE PAYMENT SKIPPED")

        return False

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    try:

        cursor.execute("""

            INSERT INTO payments (

                message,
                amount,
                name,
                whatsapp_datetime,
                status,
                paid_amount,
                paid_date,
                remarks,
                scanned_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            data["raw_message"],
            amount,
            name,
            whatsapp_datetime,
            "Pending",
            0,
            "",
            "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ))

        conn.commit()

        print("PAYMENT REQUEST SAVED")

        return True

    except Exception as e:

        print("DATABASE ERROR:", e)

        return False

    finally:

        conn.close()


# =========================================================
# FETCH PAYMENTS
# =========================================================

def fetch_payments():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *
        FROM payments
        ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================================================
# MARK PAYMENT AS PAID
# =========================================================

def mark_as_paid(payment_id, paid_amount, remarks=""):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE payments
        SET
            status = ?,
            paid_amount = ?,
            paid_date = ?,
            remarks = ?
        WHERE id = ?

    """, (

        "Paid",
        paid_amount,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        remarks,
        payment_id

    ))

    conn.commit()

    conn.close()


# =========================================================
# CLEAR ALL PAYMENTS
# =========================================================

def clear_all_payments():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM payments")

    conn.commit()

    conn.close()