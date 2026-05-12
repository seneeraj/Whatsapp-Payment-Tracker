# WhatsApp Payment Tracker

A Streamlit-based payment tracking and reconciliation dashboard that automatically scans WhatsApp payment requests, stores them in a database, tracks pending/paid status, and exports filtered reports to Excel.

---

# Features

## WhatsApp Message Scanning

* Scan payment requests directly from WhatsApp Web
* Select specific WhatsApp chats/accounts
* Detect messages in structured format

Example supported format:

```text
PAYREQ|Amount:50000|Name:Kalu Ram
```

---

# Payment Tracking

The system automatically stores:

* Request Amount
* Customer Name
* Original WhatsApp Message
* WhatsApp Date & Time
* Scan Timestamp
* Payment Status
* Paid Amount
* Remarks

---

# Reconciliation Workflow

Track:

* Pending payments
* Paid payments
* Outstanding balances

Mark requests as:

```text
Pending → Paid
```

without losing history.

---

# Excel Export

Export:

* filtered records
* date-range records
* payment reconciliation reports

to Excel format.

---

# Smart Frontend Clear

"Hide Records" only clears the frontend table view.

It does NOT:

* delete database
* remove payment history
* remove paid status

This preserves reconciliation integrity.

---

# Technology Stack

| Technology | Purpose                 |
| ---------- | ----------------------- |
| Streamlit  | Dashboard UI            |
| Playwright | WhatsApp Web Automation |
| SQLite     | Database                |
| Pandas     | Data Processing         |
| OpenPyXL   | Excel Export            |

---

# Project Structure

```text
payment_tracker/
│
├── app.py
│
├── payments.db
│
├── requirements.txt
│
├── data/
│   └── user_data/
│
├── modules/
│   ├── whatsapp.py
│   ├── parser.py
│   ├── database.py
│   └── export_excel.py
│
└── reports/
```

---

# Installation

## 1. Clone Project

```bash
git clone <your_repo_url>
cd payment_tracker
```

---

# 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

# 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 4. Install Playwright Browser

```bash
playwright install
```

---

# Run Application

```bash
streamlit run app.py
```

---

# First-Time WhatsApp Login

On first launch:

1. WhatsApp Web will open
2. Scan QR code
3. Session will be saved automatically

Future scans can reuse saved session.

---

# Supported Payment Message Format

Recommended format:

```text
PAYREQ|Amount:50000|Name:Kalu Ram
```

Required keywords:

* `PAYREQ`
* `Amount`
* `Name`

---

# Database Fields

| Field             | Description          |
| ----------------- | -------------------- |
| id                | Record ID            |
| message           | Original message     |
| amount            | Requested amount     |
| name              | Customer/vendor name |
| whatsapp_datetime | WhatsApp timestamp   |
| status            | Pending/Paid         |
| paid_amount       | Amount paid          |
| paid_date         | Payment date         |
| remarks           | User remarks         |
| scanned_at        | App scan timestamp   |

---

# Current Workflow

## Step 1

Load WhatsApp chats

## Step 2

Select chat

## Step 3

Scan messages

## Step 4

PAYREQ messages detected automatically

## Step 5

Records stored in database

## Step 6

Mark payments as paid

## Step 7

Export filtered reports

---

# Important Notes

## WhatsApp Session

WhatsApp session is stored in:

```text
data/user_data
```

Do not delete this folder unless you want to relogin.

---

# Hide Records

"Hide Records" only clears frontend display.

Database remains intact.

---

# Duplicate Prevention

The app prevents duplicate PAYREQ insertion during rescans.

---

# Recommended Production Improvements

Future enhancements:

* Bank statement reconciliation
* Auto payment matching
* UPI transaction verification
* Scheduled background scanning
* Headless scanning mode
* Multi-user login
* Audit logs
* Dashboard analytics
* Email notifications

---

# Security Notes

This project automates WhatsApp Web using Playwright.

Use responsibly and comply with:

* WhatsApp policies
* organizational policies
* privacy regulations

---

# License

MIT License

---

# Future Vision

This project can evolve into:

```text
AI-Powered Accounts Payable & Payment Reconciliation Platform
```

with:

* WhatsApp integrations
* bank reconciliation
* vendor management
* payment analytics
* automated finance workflows
