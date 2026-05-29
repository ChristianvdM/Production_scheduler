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
        # FULL RAW SCHEDULE
        # =================================================

        df.to_excel(
            writer,
            sheet_name="Full Schedule",
            index=False
        )

        # =================================================
        # SUNDAY SERVICES
        # =================================================

        sunday_df = df[
            df["Service"] == "Sunday"
        ]

        if not sunday_df.empty:

            role_order = [

                "Director",

                "Sound Main",
                "Sound Assistant",

                "Lights Main",
                "Lights Assistant",

                "Resi Main",
                "Resi Assistant"
            ]

            campuses = sorted(
                sunday_df["Campus"].unique()
            )

            combined = pd.DataFrame()

            for campus in campuses:

                campus_df = sunday_df[
                    sunday_df["Campus"] == campus
                ]

                pivot = campus_df.pivot_table(

                    index="Role",

                    columns="Date",

                    values="Volunteer",

                    aggfunc="first"
                )

                pivot = pivot.reindex(
                    role_order
                )

                pivot = pivot.reset_index()

                spacer = pd.DataFrame(
                    [[""] * len(pivot.columns)],
                    columns=pivot.columns
                )

                title = pd.DataFrame(

                    [[f"{campus} Sunday Services"]
                     + [""] * (
                        len(pivot.columns) - 1
                    )],

                    columns=pivot.columns
                )

                combined = pd.concat([
                    combined,
                    title,
                    pivot,
                    spacer
                ])

            combined.to_excel(
                writer,
                sheet_name="Sunday Services",
                index=False
            )

        # =================================================
        # PRAYER NIGHTS
        # =================================================

        prayer_df = df[
            df["Service"] == "Prayer"
        ]

        if not prayer_df.empty:

            prayer_roles = [

                "Director",

                "Sound",

                "Lights",

                "Resi",

                "Assistant"
            ]

            pivot = prayer_df.pivot_table(

                index="Role",

                columns="Date",

                values="Volunteer",

                aggfunc="first"
            )

            pivot = pivot.reindex(
                prayer_roles
            )

            pivot.to_excel(
                writer,
                sheet_name="Prayer Nights"
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

            elif sheet_name == "Prayer Nights":

                current_df = pivot.reset_index()

            elif sheet_name == "Sunday Services":

                current_df = combined

            else:

                current_df = df

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

                    ) + 2

                except:

                    max_len = 20

                worksheet.set_column(
                    idx,
                    idx,
                    max_len
                )

    output.seek(0)

    return output.getvalue()
