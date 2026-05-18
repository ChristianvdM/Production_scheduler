import pandas as pd

from scheduler.optimizer import CAMPUSES

# -------------------------------------------------
# AUTO COLUMN WIDTH
# -------------------------------------------------

def autosize_worksheet(
    worksheet,
    dataframe
):

    for idx, col in enumerate(dataframe.columns):

        try:

            max_len = max(
                dataframe[col]
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
            min(max_len, 40)
        )

# -------------------------------------------------
# FORMAT WORKSHEET
# -------------------------------------------------

def format_schedule_sheet(
    workbook,
    worksheet,
    dataframe
):

    # ---------------------------------------------
    # FORMATS
    # ---------------------------------------------

    header_format = workbook.add_format({

        "bold": True,
        "bg_color": "#1F1F1F",
        "font_color": "white",
        "align": "center",
        "valign": "vcenter",
        "border": 1
    })

    role_format = workbook.add_format({

        "bold": True,
        "bg_color": "#2B2B2B",
        "font_color": "white",
        "border": 1
    })

    cell_format = workbook.add_format({

        "border": 1,
        "align": "center",
        "valign": "vcenter"
    })

    # ---------------------------------------------
    # HEADER ROW
    # ---------------------------------------------

    for col_num, value in enumerate(
        dataframe.columns.values
    ):

        worksheet.write(
            0,
            col_num,
            value,
            header_format
        )

    # ---------------------------------------------
    # DATA CELLS
    # ---------------------------------------------

    for row in range(len(dataframe)):

        for col in range(len(dataframe.columns)):

            value = dataframe.iloc[
                row,
                col
            ]

            if col == 0:

                worksheet.write(
                    row + 1,
                    col,
                    value,
                    role_format
                )

            else:

                worksheet.write(
                    row + 1,
                    col,
                    value,
                    cell_format
                )

    # ---------------------------------------------
    # FREEZE PANES
    # ---------------------------------------------

    worksheet.freeze_panes(1, 1)

    # ---------------------------------------------
    # ROW HEIGHT
    # ---------------------------------------------

    for row_num in range(
        len(dataframe) + 1
    ):

        worksheet.set_row(
            row_num,
            28
        )

# -------------------------------------------------
# BUILD CAMPUS SHEET
# -------------------------------------------------

def build_campus_schedule(
    assignments,
    campus
):

    campus_df = assignments[
        assignments["Campus"] == campus
    ].copy()

    if campus_df.empty:
        return pd.DataFrame()

    # ---------------------------------------------
    # KEEP ORIGINAL DATE LABELS
    # ---------------------------------------------

    campus_df["Date"] = campus_df[
        "Date"
    ].astype(str)

    # ---------------------------------------------
    # ROLE ORDER
    # ---------------------------------------------

    role_order = [

        "Director",

        "Sound",
        "Sound Assistant",

        "Lights",

        "Resi",

        "Runner"
    ]

    # ---------------------------------------------
    # PIVOT
    # ---------------------------------------------

    pivot = campus_df.pivot_table(

        index="Role",

        columns="Date",

        values="Person",

        aggfunc="first"
    )

    pivot = pivot.reindex(
        role_order
    )

    pivot = pivot.fillna("")

    pivot = pivot.reset_index()

    return pivot

# -------------------------------------------------
# BUILD SUMMARY
# -------------------------------------------------

def build_summary_sheet(
    summary
):

    if summary.empty:
        return pd.DataFrame()

    ordered_columns = [

        "Person",

        "Total Assignments",

        "Tygerberg",
        "Stellies",
        "Paarl",

        "Target Assignments",

        "Fairness Delta"
    ]

    existing = [

        c for c in ordered_columns

        if c in summary.columns
    ]

    summary = summary[
        existing
    ].copy()

    return summary

# -------------------------------------------------
# BUILD DETAILED ASSIGNMENTS
# -------------------------------------------------

def build_detailed_sheet(
    assignments
):

    detailed = assignments.copy()

    if detailed.empty:
        return detailed

    detailed["Date"] = detailed[
        "Date"
    ].astype(str)

    detailed = detailed.sort_values([

        "Date",
        "Campus",
        "Role"
    ])

    return detailed

# -------------------------------------------------
# MAIN EXPORT
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

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        # =========================================
        # CAMPUS SHEETS
        # =========================================

        for campus in CAMPUSES:

            campus_schedule = (
                build_campus_schedule(
                    assignments,
                    campus
                )
            )

            if campus_schedule.empty:
                continue

            sheet_name = campus[:31]

            campus_schedule.to_excel(

                writer,

                sheet_name=sheet_name,

                index=False
            )

            worksheet = writer.sheets[
                sheet_name
            ]

            format_schedule_sheet(
                workbook,
                worksheet,
                campus_schedule
            )

            autosize_worksheet(
                worksheet,
                campus_schedule
            )

        # =========================================
        # SUMMARY SHEET
        # =========================================

        summary_sheet = build_summary_sheet(
            summary
        )

        summary_sheet.to_excel(

            writer,

            sheet_name="Summary",

            index=False
        )

        worksheet = writer.sheets[
            "Summary"
        ]

        format_schedule_sheet(
            workbook,
            worksheet,
            summary_sheet
        )

        autosize_worksheet(
            worksheet,
            summary_sheet
        )

        # =========================================
        # DETAILED ASSIGNMENTS
        # =========================================

        detailed_sheet = (
            build_detailed_sheet(
                assignments
            )
        )

        detailed_sheet.to_excel(

            writer,

            sheet_name="All Assignments",

            index=False
        )

        worksheet = writer.sheets[
            "All Assignments"
        ]

        format_schedule_sheet(
            workbook,
            worksheet,
            detailed_sheet
        )

        autosize_worksheet(
            worksheet,
            detailed_sheet
        )

        # =========================================
        # METADATA SHEET
        # =========================================

        metadata = pd.DataFrame({

            "Metric": [

                "Generated Assignments",
                "Unique Volunteers",
                "Campuses"
            ],

            "Value": [

                len(assignments),

                assignments["Person"]
                .nunique(),

                len(CAMPUSES)
            ]
        })

        metadata.to_excel(

            writer,

            sheet_name="Metadata",

            index=False
        )

        worksheet = writer.sheets[
            "Metadata"
        ]

        format_schedule_sheet(
            workbook,
            worksheet,
            metadata
        )

        autosize_worksheet(
            worksheet,
            metadata
        )
