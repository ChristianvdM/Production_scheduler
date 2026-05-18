import pandas as pd


def load_dataframe(uploaded_file):

    """
    Load CSV, XLSX, or ODS files into a pandas DataFrame.
    """

    ext = uploaded_file.name.split(".")[-1].lower()

    # -------------------------------------------------
    # CSV
    # -------------------------------------------------

    if ext == "csv":

        df = pd.read_csv(
            uploaded_file
        )

    # -------------------------------------------------
    # EXCEL
    # -------------------------------------------------

    elif ext in ["xlsx", "xls"]:

        df = pd.read_excel(
            uploaded_file
        )

    # -------------------------------------------------
    # ODS
    # -------------------------------------------------

    elif ext == "ods":

        df = pd.read_excel(
            uploaded_file,
            engine="odf"
        )

    # -------------------------------------------------
    # INVALID TYPE
    # -------------------------------------------------

    else:

        raise ValueError(
            f"Unsupported file type: {ext}"
        )

    # -------------------------------------------------
    # CLEAN COLUMN NAMES
    # -------------------------------------------------

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    # -------------------------------------------------
    # CLEAN NAME COLUMN
    # -------------------------------------------------

    if "Name" in df.columns:

        df["Name"] = (
            df["Name"]
            .astype(str)
            .str.strip()
        )

    # -------------------------------------------------
    # REMOVE EMPTY ROWS
    # -------------------------------------------------

    df = df.dropna(
        how="all"
    )

    # -------------------------------------------------
    # REPLACE NaN VALUES
    # -------------------------------------------------

    df = df.fillna(0)

    # -------------------------------------------------
    # CLEAN NUMERIC COLUMNS
    # -------------------------------------------------

    for col in df.columns:

        if col == "Name":
            continue

        try:

            df[col] = pd.to_numeric(
                df[col],
                errors="ignore"
            )

        except:
            pass

    return df
