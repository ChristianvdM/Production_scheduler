import pandas as pd

CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]


# -------------------------------------------------
# AUTO SIZE COLUMNS
# -------------------------------------------------

def autosize_worksheet(
    worksheet,
    dataframe
):

    for idx, col in enumerate(
        dataframe.columns
    ):

        try:

            max_length = max(

                dataframe[col]
                .astype(str)
                .map(len)
                .max(),

                len(str(col))

            ) + 3

        except:

            max_length = 20

        worksheet.set_column(
            idx,
            idx,
            max_length
        )


# -------------------------------------------------
# BUILD EXCEL OUTPUT
# -------------------------------------------------

def build_excel_output(
    schedule_result,
    output
):

    assignments = schedule_result[
        "assignments"
    ]

    summary = schedule_result[
        "summary"
    ]

    logs = schedule_result.get(
        "logs",
        []
    )

    # -------------------------------------------------
    # EMPTY SAFETY
    # -------------------------------------------------

    if assignments.empty:

        with pd.ExcelWriter(
            output,
            engine="xlsxwriter"
        ) as writer:

            pd.DataFrame({
                "Message": [
                    "No assignments generated"
                ]
            }).to_excel(
                writer,
                sheet_name="Empty",
                index=False
            )

        return

    # -------------------------------------------------
    # EXCEL WRITER
    # -------------------------------------------------

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        # -------------------------------------------------
        # FORMATS
        # -------------------------------------------------

        header_format = workbook.add_format({

            "bold": True,

            "bg_color": "#222222",

            "font_color": "white",

            "border": 1
        })

        # -------------------------------------------------
        # FULL ASSIGNMENTS
        # -------------------------------------------------

        assignments_export = assignments.sort_values(

            by=[
                "Date",
                "Campus",
                "Role"
            ]
        )

        assignments_export.to_excel(

            writer,

            sheet_name="Assignments",

            index=False
        )

        worksheet = writer.sheets[
            "Assignments"
        ]

        autosize_worksheet(
            worksheet,
            assignments_export
        )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        if not summary.empty:

            summary_export = summary.sort_values(
                by="Total Assignments",
                ascending=False
            )

            summary_export.to_excel(

                writer,

                sheet_name="Summary",

                index=False
            )

            worksheet = writer.sheets[
                "Summary"
            ]

            autosize_worksheet(
                worksheet,
                summary_export
            )

        # -------------------------------------------------
        # CAMPUS SHEETS
        # -------------------------------------------------

        for campus in CAMPUSES:

            campus_df = assignments[
                assignments["Campus"]
                == campus
            ].copy()

            if campus_df.empty:
                continue

            campus_df = campus_df.sort_values(

                by=[
                    "Date",
                    "Service",
                    "Role"
                ]
            )

            export_df = campus_df[

                [
                    "Date",
                    "Service",
                    "Role",
                    "Person",
                    "Skill",
                    "Score"
                ]

            ]

            sheet_name = campus[:31]

            export_df.to_excel(

                writer,

                sheet_name=sheet_name,

                index=False
            )

            worksheet = writer.sheets[
                sheet_name
            ]

            autosize_worksheet(
                worksheet,
                export_df
            )

        # -------------------------------------------------
        # SERVICE SHEETS
        # -------------------------------------------------

        if "Service" in assignments.columns:

            service_types = assignments[
                "Service"
            ].unique()

            for service in service_types:

                service_df = assignments[

                    assignments["Service"]
                    == service

                ].copy()

                if service_df.empty:
                    continue

                service_export = service_df[

                    [
                        "Date",
                        "Campus",
                        "Role",
                        "Person",
                        "Skill",
                        "Score"
                    ]

                ].sort_values(

                    by=[
                        "Date",
                        "Campus",
                        "Role"
                    ]
                )

                sheet_name = (
                    f"{service}_Services"
                )[:31]

                service_export.to_excel(

                    writer,

                    sheet_name=sheet_name,

                    index=False
                )

                worksheet = writer.sheets[
                    sheet_name
                ]

                autosize_worksheet(
                    worksheet,
                    service_export
                )

        # -------------------------------------------------
        # FAIRNESS REPORT
        # -------------------------------------------------

        if not summary.empty:

            fairness_columns = [

                c for c in summary.columns

                if c in CAMPUSES
            ]

            fairness_report = summary[

                [
                    "Person",
                    "Total Assignments",
                    "Target Assignments",
                    "Fairness Delta"
                ] + fairness_columns

            ]

            fairness_report.to_excel(

                writer,

                sheet_name="Fairness",

                index=False
            )

            worksheet = writer.sheets[
                "Fairness"
            ]

            autosize_worksheet(
                worksheet,
                fairness_report
            )

        # -------------------------------------------------
        # LOG SHEET
        # -------------------------------------------------

        if logs:

            logs_df = pd.DataFrame({

                "Scheduler Logs": logs
            })

            logs_df.to_excel(

                writer,

                sheet_name="Logs",

                index=False
            )

            worksheet = writer.sheets[
                "Logs"
            ]

            autosize_worksheet(
                worksheet,
                logs_df
            )

        # -------------------------------------------------
        # HEADER FORMATTING
        # -------------------------------------------------

        for sheet_name in writer.sheets:

            worksheet = writer.sheets[
                sheet_name
            ]

            worksheet.freeze_panes(1, 0)

            worksheet.set_zoom(90)

            try:

                sheet_df = pd.read_excel(
                    output,
                    sheet_name=sheet_name
                )

                for col_num, value in enumerate(
                    sheet_df.columns
                ):

                    worksheet.write(
                        0,
                        col_num,
                        value,
                        header_format
                    )

            except:
                pass
