import pandas as pd
from io import BytesIO


def export_schedule(assignments):

    rows = []

    for a in assignments:

        rows.append({
            "Date": a.date,
            "Campus": a.campus,
            "ServiceType": a.service_type,
            "Role": a.role,
            "Volunteer": a.volunteer
        })

    df = pd.DataFrame(rows)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        df.to_excel(writer, sheet_name="Schedule", index=False)

        summary = (
            df.groupby(["Volunteer", "Campus"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )

        summary["Total"] = summary.drop(
            columns=["Volunteer"]
        ).sum(axis=1)

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

    return output.getvalue()
