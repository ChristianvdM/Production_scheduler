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

    worksheet.freeze_panes(1, 1)

# -------------------------------------------------
# BUILD CAMPUS SHEET
# -------------------------------------------------

def build_campus_schedule(
    assignments,
    campus,
    date_order
):

    campus_df = assignments[

        (assignments["Campus"] == campus)

        &

        (assignments["Service"] == "Sunday")

    ].copy()

    if campus_df.empty:
        return pd.DataFrame()

    role_order = [

        "Director",

        "Sound",
        "Sound Assistant",

        "Lights",

        "Resi"
    ]

    pivot = campus_df.pivot_table(

        index="Role",

        columns="Date",

        values="Person",

        aggfunc="first"
    )

    existing_dates = [

        d for d in date_order

        if d in pivot.columns
    ]

    pivot = pivot.reindex(
        columns=existing_dates
    )

    pivot = pivot.reindex(
        role_order
    )

    pivot = pivot.fillna("")

    pivot = pivot.reset_index()

    return pivot

# -------------------------------------------------
# BUILD PRAYER SHEET
# -------------------------------------------------

def build_prayer_schedule(
    assignments,
    date_order
):

    prayer_df = assignments[

        assignments["Service"] == "Prayer"

    ].copy()

    if prayer_df.empty:
        return pd.DataFrame()

    role_order = [

        "Sound",

        "Sound Assistant",

        "Runner"
    ]

    prayer_df["Role_Display"] = prayer_df.groupby(
        ["Date", "Role"]
    ).cumcount() + 1

    prayer_df["Role_Display"] = prayer_df.apply(

        lambda row:

        f"{row['Role']} {row['Role_Display']}"

        if row["Role"] == "Sound Assistant"

        else row["Role"],

        axis=1
    )

    pivot = prayer_df.pivot_table(

        index="Role_Display",

        columns="Date",

        values="Person",

        aggfunc="first"
    )

    existing_dates = [

        d for d in date_order

        if d in pivot.columns
    ]

    pivot = pivot.reindex(
        columns=existing_dates
    )

    desired_order = [

        "Sound",

        "Sound Assistant 1",
        "Sound Assistant 2",

        "Runner"
    ]

    pivot = pivot.reindex(
        desired_order
    )

    pivot = pivot.fillna("")

    pivot = pivot.reset_index()

    pivot.rename(
        columns={
            "Role_Display": "Role"
        },
        inplace=True
    )

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

        "Prayer",

        "Target Assignments",

        "Fairness Delta"
    ]

    existing = [

        c for c in ordered_columns

        if c in summary.columns
    ]

    return summary[
        existing
    ].copy()

# -------------------------------------------------
# BUILD DETAILED SHEET
# -------------------------------------------------

def build_detailed_sheet(
    assignments
):

    detailed = assignments.copy()

    if detailed.empty:
        return detailed

    return detailed.sort_values([

        "Date",
        "Service",
        "Campus",
        "Role"
    ])

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

    date_order = schedule_result.get(
        "date_order",
        []
    )

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
                    campus,
                    date_order
                )
            )

            if campus_schedule.empty:
                continue

            campus_schedule.to_excel(

                writer,

                sheet_name=campus,

                index=False
            )

            worksheet = writer.sheets[
                campus
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
        # PRAYER SHEET
        # =========================================

        prayer_schedule = (
            build_prayer_schedule(
                assignments,
                date_order
            )
        )

        if not prayer_schedule.empty:

            prayer_schedule.to_excel(

                writer,

                sheet_name="Prayer",

                index=False
            )

            worksheet = writer.sheets[
                "Prayer"
            ]

            format_schedule_sheet(
                workbook,
                worksheet,
                prayer_schedule
            )

            autosize_worksheet(
                worksheet,
                prayer_schedule
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
