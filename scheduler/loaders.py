import pandas as pd
import re

# -------------------------------------------------
# LOAD DATAFRAME
# -------------------------------------------------

def load_dataframe(uploaded_file):

    filename = uploaded_file.name.lower()

    # ---------------------------------------------
    # CSV
    # ---------------------------------------------

    if filename.endswith(".csv"):

        df = pd.read_csv(uploaded_file)

    # ---------------------------------------------
    # XLSX
    # ---------------------------------------------

    elif filename.endswith(".xlsx"):

        df = pd.read_excel(
            uploaded_file,
            sheet_name=0
        )

    # ---------------------------------------------
    # ODS
    # ---------------------------------------------

    elif filename.endswith(".ods"):

        df = pd.read_excel(
            uploaded_file,
            engine="odf",
            sheet_name=0
        )

    else:

        raise ValueError(
            "Unsupported file format"
        )

    # ---------------------------------------------
    # CLEAN COLUMN NAMES
    # ---------------------------------------------

    df.columns = [

        str(c).strip()

        for c in df.columns
    ]

    # ---------------------------------------------
    # REMOVE UNNAMED COLUMNS
    # ---------------------------------------------

    df = df.loc[
        :,
        ~df.columns.str.contains("^Unnamed")
    ]

    # ---------------------------------------------
    # AVAILABILITY FILE CLEANING
    # ---------------------------------------------

    if "availability" in filename:

        cleaned_columns = []

        for col in df.columns:

            if col == "Name":

                cleaned_columns.append(col)

                continue

            # -------------------------------------
            # STRICT MATCH:
            # 23 May - Prayer
            # 24 May - Services
            # -------------------------------------

            match = re.match(

                r"^\d{1,2}\s+[A-Za-z]+\s*-\s*(Prayer|Services)$",

                str(col).strip()
            )

            if match:

                cleaned_columns.append(
                    col
                )

        # -----------------------------------------
        # KEEP ONLY VALID DATE COLUMNS
        # -----------------------------------------

        df = df[
            cleaned_columns
        ]

    # ---------------------------------------------
    # DROP EMPTY ROWS
    # ---------------------------------------------

    df = df.dropna(
        how="all"
    )

    return df
