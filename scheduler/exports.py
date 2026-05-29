import pandas as pd

from io import BytesIO


# =========================================================
# EXPORT SCHEDULE
# =========================================================

def export_schedule(assignments):

    output = BytesIO()

    rows = []

    for a in assignments:

        rows.append({

            "Date": a.date,

            "Campus": a.campus,

            "Service": a.service_type,

            "Role": a.role,

            "Volunteer": a.volunteer
        })

    df = pd.DataFrame(rows)

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        # =================================================
        # FULL SCHEDULE
        # =================================================

        df.to_excel(
            writer,
            sheet_name="Full Schedule",
            index=False
        )

        # =================================================
        # ONE SHEET PER SERVICE
        # =================================================

        unique_dates = df["Date"].unique()

        for service_date in unique_dates:

            service_df = df[
                df["Date"] == service_date
            ]

            sheet_name = (
                str(service_date)
                .replace("/", "-")
            )[:31]

            export_rows = []

            campuses = service_df[
                "Campus"
            ].unique()

            for campus in campuses:

                campus_df = service_df[
                    service_df["Campus"]
                    == campus
                ]

                export_rows.append({
                    "Role": f"{campus}",
                    "Volunteer": ""
                })

                for _, row in (
                    campus_df.iterrows()
                ):

                    export_rows.append({

                        "Role":
                            row["Role"],

                        "Volunteer":
                            row["Volunteer"]
                    })

                export_rows.append({
                    "Role": "",
                    "Volunteer": ""
                })

            export_df = pd.DataFrame(
                export_rows
            )

            export_df.to_excel(

                writer,

                sheet_name=sheet_name,

                index=False
            )

        # =================================================
        # SUMMARY
        # =================================================

        summary = (

            df.groupby(
                ["Volunteer", "Campus"]
            )

            .size()

            .unstack(fill_value=0)

            .reset_index()
        )

        campus_cols = [

            c for c in summary.columns

            if c != "Volunteer"
        ]

        summary[
            "Total Assignments"
        ] = summary[
            campus_cols
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
        # AUTO WIDTHS
        # =================================================

        for sheet_name in writer.sheets:

            worksheet = writer.sheets[
                sheet_name
            ]

            if sheet_name == "Summary":

                current_df = summary

            elif sheet_name == "Full Schedule":

                current_df = df

            else:

                current_df = export_df

            for idx, col in enumerate(
                current_df.columns
            ):

                try:

                    max_len = max(

                        current_df[col]
                        .astype(str)
                        .map(len)
                        .max(),

                        len(str(col))

                    ) + 3

                except:

                    max_len = 20

                worksheet.set_column(
                    idx,
                    idx,
                    max_len
                )

    output.seek(0)

    return output.getvalue()
