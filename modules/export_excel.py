import pandas as pd


# =========================================================
# EXPORT FILTERED DATAFRAME TO EXCEL
# =========================================================

def export_to_excel(df):

    # -----------------------------------------------------
    # CLEAN WHATSAPP DATETIME
    # -----------------------------------------------------

    def clean_whatsapp_datetime(value):

        try:

            cleaned = str(value)

            cleaned = cleaned.replace("[", "")

            cleaned = cleaned.replace("]", "")

            return cleaned

        except:
            return value

    if "WhatsApp DateTime" in df.columns:

        df["WhatsApp DateTime"] = df[
            "WhatsApp DateTime"
        ].apply(clean_whatsapp_datetime)

    # -----------------------------------------------------
    # REMOVE INTERNAL FILTER COLUMN
    # -----------------------------------------------------

    if "Filter Date" in df.columns:

        df = df.drop(columns=["Filter Date"])

    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------

    file_path = "payment_report.xlsx"

    df.to_excel(
        file_path,
        index=False
    )

    return file_path