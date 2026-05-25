import pandas as pd
import unicodedata
import re

# ---------------------------------------------------
# NAME NORMALIZATION
# ---------------------------------------------------

def normalize_name(name):

    if pd.isna(name):
        return ""

    name = str(name)

    # Unicode normalize
    name = unicodedata.normalize(
        "NFKD",
        name
    )

    # Remove accents
    name = "".join(
        c for c in name
        if not unicodedata.combining(c)
    )

    # Lowercase
    name = name.lower()

    # Normalize apostrophes
    name = (
        name.replace("’", "'")
            .replace("`", "'")
    )

    # Collapse spaces
    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()

# ---------------------------------------------------
# LOAD DATAFRAME
# ---------------------------------------------------

def load_dataframe(file):

    filename = file.name.lower()

    if filename.endswith(".csv"):

        df = pd.read_csv(file)

    elif filename.endswith(".xlsx"):

        df = pd.read_excel(file)

    elif filename.endswith(".ods"):

        df = pd.read_excel(
            file,
            engine="odf"
        )

    else:

        raise ValueError(
            "Unsupported file format"
        )

    # ---------------------------------------------------
    # CLEAN NAME COLUMN
    # ---------------------------------------------------

    if "Name" in df.columns:

        df["Name"] = (
            df["Name"]
            .astype(str)
            .str.strip()
        )

        df["Name_Normalized"] = (
            df["Name"]
            .apply(normalize_name)
        )

    return df
