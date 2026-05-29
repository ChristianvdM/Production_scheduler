import pandas as pd

from io import BytesIO


# =========================================================
# EXPORT SCHEDULE
# =========================================================

def export_schedule(assignments):

    rows = []

    # =====================================================
    # BUILD ROWS
    # =====================================================

    for a in assignments:

        rows.append({

            "Date":
                a.date,

            "Campus":
                a.campus,

            "ServiceType":
                a.service_type,

            "Role":
                a.role,

            "Volunteer":
                a.volunteer
        })

    # =====================================================
    # CREATE DATAFRAME
    # =====================================================

    df = pd.DataFrame(rows)

    output = BytesIO()

    # =====================================================
    # EXCEL EXPORT
    # =====================================================

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        # =================================================
        # MAIN SCHEDULE SHEET
        # =================================================

        df.to_excel(
            writer,
            sheet_name="Schedule",
            index=False
        )

        # =================================================
        # SUMMARY SHEET
        # =================================================

        if not df.empty:

            summary = (

                df.groupby(
                    ["Volunteer", "Campus"]
                )

                .size()

                .unstack(fill_value=0)

                .reset_index()
            )

            campus_columns = [

                c for c in summary.columns

                if c != "Volunteer"
            ]

            summary[
                "Total Assignments"
            ] = summary[
                campus_columns
            ].sum(axis=1)

            summary = summary.sort_values(
                by="Total Assignments",
                ascending=False
            )

            summary.to_excel(
                writer,
                sheet_name="Summary",
                index=False
            )

        # =================================================
        # AUTO COLUMN WIDTHS
        # =================================================

        for sheet_name in writer.sheets:

            worksheet = writer.sheets[
                sheet_name
            ]

            if sheet_name == "Schedule":

                current_df = df

            else:

                current_df = summary

            for idx, col in enumerate(
                current_df.columns
            ):

                max_len = max(
                    current_df[col]
                    .astype(str)
                    .map(len)
                    .max(),

                    len(str(col))
                ) + 2

                worksheet.set_column(
                    idx,
                    idx,
                    max_len
                )

    output.seek(0)

    return output.getvalue()import pandas as pd
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
