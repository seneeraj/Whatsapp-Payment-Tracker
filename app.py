import streamlit as st
import pandas as pd
from datetime import date

from modules.database import (
    init_db,
    fetch_payments,
    mark_as_paid
)

from modules.whatsapp import (
    get_whatsapp_chats,
    scan_selected_chat
)

from modules.export_excel import export_to_excel


# =========================================================
# INIT DATABASE
# =========================================================

init_db()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="WhatsApp Payment Tracker",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    .title-box {
        background: linear-gradient(90deg, #25D366, #128C7E);
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 15px;
    }

    .metric-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "whatsapp_chats" not in st.session_state:
    st.session_state.whatsapp_chats = []

if "hide_records" not in st.session_state:
    st.session_state.hide_records = False


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class='title-box'>
        <h2>💰 WhatsApp Payment Tracker</h2>
        <p>
        Payment Request Tracking & Reconciliation Dashboard
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📲 WhatsApp")

    st.markdown("---")

    # =====================================================
    # LOAD CHATS
    # =====================================================

    if st.button(
        "Load WhatsApp Chats",
        width="stretch"
    ):

        with st.spinner("Loading chats..."):

            chats = get_whatsapp_chats()

            st.session_state.whatsapp_chats = chats

        st.success(f"{len(chats)} chats loaded")

    # =====================================================
    # CHAT SELECTION
    # =====================================================

    if len(st.session_state.whatsapp_chats) > 0:

        selected_chat = st.selectbox(
            "Select WhatsApp Account",
            st.session_state.whatsapp_chats
        )

        if st.button(
            "Scan Selected Chat",
            width="stretch"
        ):

            with st.spinner("Scanning messages..."):

                scan_selected_chat(selected_chat)

            st.session_state.hide_records = False

            st.success("Scan completed")

            st.rerun()

    st.markdown("---")

    st.subheader("⚙️ Actions")

    # =====================================================
    # HIDE RECORDS (FRONTEND ONLY)
    # =====================================================

    if st.button(
        "Scan Again",
        width="stretch"
    ):

        st.session_state.hide_records = True

        st.rerun()


# =========================================================
# PAYMENT RECORDS
# =========================================================

if st.session_state.hide_records:

    rows = []

else:

    rows = fetch_payments()


if rows:

    columns = [
        "ID",
        "Message",
        "Amount",
        "Name",
        "WhatsApp DateTime",
        "Status",
        "Paid Amount",
        "Paid Date",
        "Remarks",
        "Scanned At"
    ]

    df = pd.DataFrame(rows, columns=columns)

    # =====================================================
    # EXTRACT DATE
    # =====================================================

    def extract_whatsapp_date(value):

        try:

            cleaned = str(value)

            cleaned = cleaned.replace("[", "")

            cleaned = cleaned.split("]")[0]

            parts = cleaned.split(",")

            if len(parts) >= 2:

                date_part = parts[1].strip()

                return pd.to_datetime(
                    date_part,
                    format="%d/%m/%Y",
                    errors="coerce"
                ).date()

        except:
            return None

        return None

    df["Filter Date"] = df[
        "WhatsApp DateTime"
    ].apply(extract_whatsapp_date)

    # =====================================================
    # FILTERS
    # =====================================================

    top_col1, top_col2, top_col3 = st.columns([1, 1, 1])

    today = date.today()

    with top_col1:

        start_date = st.date_input(
            "Start Date",
            value=today
        )

    with top_col2:

        end_date = st.date_input(
            "End Date",
            value=today
        )

    # =====================================================
    # APPLY FILTER
    # =====================================================

    filtered_df = df[
        (df["Filter Date"] >= start_date)
        &
        (df["Filter Date"] <= end_date)
    ]

    # =====================================================
    # EXPORT BUTTON
    # =====================================================

    with top_col3:

        try:

            file_path = export_to_excel(filtered_df)

            with open(file_path, "rb") as f:

                excel_data = f.read()

            st.download_button(
                label="📊 Download Report",
                data=excel_data,
                file_name="payment_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

        except Exception as export_error:

            st.error(export_error)

    # =====================================================
    # METRICS
    # =====================================================

    total_requests = len(filtered_df)

    total_amount = filtered_df["Amount"].sum()

    total_paid = filtered_df[
        filtered_df["Status"] == "Paid"
    ]["Paid Amount"].sum()

    pending_amount = total_amount - total_paid

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Requests", total_requests)

    with m2:
        st.metric("Requested", f"₹ {total_amount:,}")

    with m3:
        st.metric("Paid", f"₹ {total_paid:,}")

    with m4:
        st.metric("Pending", f"₹ {pending_amount:,}")

    st.markdown("---")

    # =====================================================
    # PAYMENT TABLE
    # =====================================================

    st.subheader("📋 Payment Records")

    st.dataframe(
        filtered_df,
        width="stretch",
        height=420
    )

    st.markdown("---")

    # =====================================================
    # MARK PAYMENT AS PAID
    # =====================================================

    st.subheader("✅ Mark Payment As Paid")

    pending_df = filtered_df[
        filtered_df["Status"] == "Pending"
    ]

    if len(pending_df) > 0:

        payment_options = {
            f"ID {row['ID']} | {row['Name']} | ₹{row['Amount']}": row['ID']
            for _, row in pending_df.iterrows()
        }

        selected_payment = st.selectbox(
            "Select Pending Payment",
            list(payment_options.keys())
        )

        selected_id = payment_options[selected_payment]

        selected_row = pending_df[
            pending_df["ID"] == selected_id
        ].iloc[0]

        d1, d2 = st.columns(2)

        with d1:

            st.info(f"""
            👤 Name: {selected_row['Name']}

            💰 Requested Amount:
            ₹ {selected_row['Amount']:,}

            📌 Status:
            {selected_row['Status']}
            """)

        with d2:

            st.info(f"""
            🕒 WhatsApp DateTime:
            {selected_row['WhatsApp DateTime']}

            📥 Scanned At:
            {selected_row['Scanned At']}
            """)

        paid_amount = st.number_input(
            "Paid Amount",
            min_value=0,
            value=int(selected_row["Amount"]),
            step=1
        )

        remarks = st.text_input("Remarks")

        if st.button(
            "💸 Mark As Paid",
            width="stretch"
        ):

            mark_as_paid(
                selected_id,
                paid_amount,
                remarks
            )

            st.success("Payment marked as PAID")

            st.rerun()

    else:

        st.info("No pending payments available.")

else:

    st.info("No payment records found.")