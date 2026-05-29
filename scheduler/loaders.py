import pandas as pd
from pyexcel_ods3 import get_data
from scheduler.models import HistoricalAssignment


def load_file(uploaded_file):

    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    elif filename.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)

    elif filename.endswith(".ods"):
        data = get_data(uploaded_file)
        first_sheet = list(data.keys())[0]
        rows = data[first_sheet]

        headers = rows[0]
        values = rows[1:]

        return pd.DataFrame(values, columns=headers)

    else:
        raise ValueError("Unsupported file format")


def normalize_names(df):
    if "Name" in df.columns:
        df["Name"] = df["Name"].astype(str).str.strip()

    return df


def load_skills(file):
    df = load_file(file)
    return normalize_names(df)


def load_availability(file):
    df = load_file(file)
    return normalize_names(df)


def load_actual_schedule(file):

    if file is None:
        return []

    df = load_file(file)

    required_columns = [
        "Name",
        "Campus",
        "Role",
        "ServiceType",
        "Date",
        "Served"
    ]

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in actual schedule file: {missing}")

    history = []

    for _, row in df.iterrows():

        history.append(
            HistoricalAssignment(
                volunteer=str(row["Name"]).strip(),
                campus=row["Campus"],
                role=row["Role"],
                service_type=row["ServiceType"],
                date=str(row["Date"]),
                scheduled=True,
                served=str(row["Served"]).lower() == "yes"
            )
        )

    return history
