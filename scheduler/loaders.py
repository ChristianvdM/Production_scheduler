import pandas as pd


def load_dataframe(uploaded_file):

    ext = uploaded_file.name.split(".")[-1].lower()

    if ext == "csv":

        df = pd.read_csv(uploaded_file)

    elif ext in ["xlsx", "xls"]:

        df = pd.read_excel(
            uploaded_file,
            sheet_name=0
        )

    elif ext == "ods":

        df = pd.read_excel(
            uploaded_file,
            engine="odf",
            sheet_name=0
        )

    else:

        raise ValueError(
            f"Unsupported file type: {ext}"
        )

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    if "Name" in df.columns:

        df["Name"] = (
            df["Name"]
            .astype(str)
            .str.strip()
        )

    return df
