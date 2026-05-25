import pandas as pd

from scheduler.optimizer import CAMPUSES

# ---------------------------------------------------
# AUTO WIDTH
# ---------------------------------------------------

def auto_width(
    dataframe,
    worksheet
):

    for idx, col in enumerate(
        dataframe.columns
    ):

        max_len = max(

            dataframe[col]
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

# ---------------------------------------------------
# EXPORT
# ---------------------------------------------------

def build_excel_output(
    schedule_result,
    output
):

    assignments_df = (
        schedule_result["assignments"]
        .copy()
    )

    summary_df = (
        schedule_result["summary"]
        .copy()
    )

    assignments_df = assignments_df.drop(
        columns=["Name_Normalized"],
        errors="ignore"
    )

    summary_df = summary_df.drop(
        columns=["Name_Normalized"],
        errors="ignore"
    )

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        assignments_df.to_excel(
            writer,
            sheet_name="Assignments",
            index=False
        )

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        auto_width(
            assignments_df,
            writer.sheets["Assignments"]
        )

        auto_width(
            summary_df,
            writer.sheets["Summary"]
        )
