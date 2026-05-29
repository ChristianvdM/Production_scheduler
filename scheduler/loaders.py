import pandas as pd

from pyexcel_ods3 import get_data

from scheduler.models import (
    HistoricalAssignment
)


# =========================================================
# GENERIC FILE LOADER
# =========================================================

def load_file(uploaded_file):

    filename = uploaded_file.name.lower()

    # =====================================================
    # CSV
    # =====================================================

    if filename.endswith(".csv"):

        return pd.read_csv(
            uploaded_file
        )

    # =====================================================
    # XLSX
    # =====================================================

    elif filename.endswith(".xlsx"):

        return pd.read_excel(
            uploaded_file
        )

    # =====================================================
    # ODS
    # =====================================================

    elif filename.endswith(".ods"):

        data = get_data(
            uploaded_file
        )

        first_sheet = list(
            data.keys()
        )[0]

        rows = data[first_sheet]

        # =================================================
        # REMOVE FULLY EMPTY ROWS
        # =================================================

        rows = [

            row for row in rows

            if any(
                str(cell).strip()
                for cell in row
            )
        ]

        if not rows:

            raise ValueError(
                "ODS file is empty"
            )

        # =================================================
        # HEADERS
        # =================================================

        headers = [
            str(h).strip()
            for h in rows[0]
        ]

        values = rows[1:]

        cleaned_rows = []

        header_len = len(headers)

        # =================================================
        # NORMALIZE ROW LENGTHS
        # =================================================

        for row in values:

            row = list(row)

            # ---------------------------------------------
            # PAD SHORT ROWS
            # ---------------------------------------------

            if len(row) < header_len:

                row.extend(
                    [None] * (
                        header_len - len(row)
                    )
                )

            # ---------------------------------------------
            # TRIM LONG ROWS
            # ---------------------------------------------

            elif len(row) > header_len:

                row = row[:header_len]

            cleaned_rows.append(row)

        # =================================================
        # CREATE DATAFRAME
        # =================================================

        return pd.DataFrame(
            cleaned_rows,
            columns=headers
        )

    # =====================================================
    # INVALID FILE TYPE
    # =====================================================

    else:

        raise ValueError(
            "Unsupported file format"
        )


# =========================================================
# NORMALIZE NAMES
# =========================================================

def normalize_names(df):

    if "Name" in df.columns:

        df["Name"] = (
            df["Name"]
            .astype(str)
            .str.strip()
        )

    return df


# =========================================================
# LOAD SKILLS
# =========================================================

def load_skills(file):

    df = load_file(file)

    return normalize_names(df)


# =========================================================
# LOAD AVAILABILITY
# =========================================================

def load_availability(file):

    df = load_file(file)

    return normalize_names(df)


# =========================================================
# LOAD HISTORICAL ACTUAL SCHEDULE
# =========================================================

def load_actual_schedule(file):

    if file is None:

        return []

    df = load_file(file)

    required_columns = [

        "Name",
        "Campus",
        "Role",
        "ServiceType",
        "Date"
    ]

    missing = [

        c for c in required_columns

        if c not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )

    history = []

    for _, row in df.iterrows():

        history.append(

            HistoricalAssignment(

                volunteer=str(
                    row["Name"]
                ).strip(),

                campus=str(
                    row["Campus"]
                ).strip(),

                role=str(
                    row["Role"]
                ).strip(),

                service_type=str(
                    row["ServiceType"]
                ).strip(),

                date=str(
                    row["Date"]
                ).strip()
            )
        )

    return history
