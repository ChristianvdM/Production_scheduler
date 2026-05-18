import pandas as pd

CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]


def autosize_worksheet(worksheet, dataframe):

    for idx, col in enumerate(dataframe.columns):

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


def build_excel_output(
    schedule_result,
    output
):

    assignments = schedule_result["assignments"]

    summary = schedule_result["summary"]

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        # -------------------------------------------------
        # FULL ASSIGNMENTS
        # -------------------------------------------------

        assignments.to_excel(
            writer,
            sheet_name="Assignments",
            index=False
        )

        assignment_sheet = writer.sheets[
            "Assignments"
        ]

        autosize_worksheet(
            assignment_sheet,
            assignments
        )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        summary_sheet = writer.sheets[
            "Summary"
        ]

        autosize_worksheet(
            summary_sheet,
            summary
        )

        # -------------------------------------------------
        # CAMPUS SHEETS
        # -------------------------------------------------

        for campus in CAMPUSES:

            campus_df = assignments[
                assignments["Campus"] == campus
            ]

            if campus_df.empty:
                continue

            pivot = campus_df.pivot_table(
                index="Role",
                columns="Date",
                values="Person",
                aggfunc="first"
            )

            pivot = pivot.fillna("")

            sheet_name = campus[:31]

            pivot.to_excel(
                writer,
                sheet_name=sheet_name
            )

            worksheet = writer.sheets[sheet_name]

            autosize_worksheet(
                worksheet,
                pivot.reset_index()
            )

        # -------------------------------------------------
        # SERVICE TYPE SHEETS
        # -------------------------------------------------

        if "Service" in assignments.columns:

            service_types = assignments[
                "Service"
            ].unique()

            for service in service_types:

                service_df = assignments[
                    assignments["Service"] == service
                ]

                if service_df.empty:
                    continue

                service_pivot = service_df.pivot_table(
                    index=["Campus", "Role"],
                    columns="Date",
                    values="Person",
                    aggfunc="first"
                )

                service_pivot = service_pivot.fillna("")

                sheet_name = f"{service}_Services"

                sheet_name = sheet_name[:31]

                service_pivot.to_excel(
                    writer,
                    sheet_name=sheet_name
                )

                worksheet = writer.sheets[
                    sheet_name
                ]

                autosize_worksheet(
                    worksheet,
                    service_pivot.reset_index()
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
        # FORMATTING
        # -------------------------------------------------

        workbook = writer.book

        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#222222",
            "font_color": "white",
            "border": 1
        })

        for sheet_name in writer.sheets:

            worksheet = writer.sheets[
                sheet_name
            ]

            worksheet.freeze_panes(1, 1)

            worksheet.set_zoom(90)

            for col_num, value in enumerate(
                assignments.columns
            ):

                try:

                    worksheet.write(
                        0,
                        col_num,
                        value,
                        header_format
                    )

                except:
                    pass
