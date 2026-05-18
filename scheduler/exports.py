import pandas as pd


CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]


def build_excel_output(
    schedule_result,
    output
):

    assignments = schedule_result['assignments']
    summary = schedule_result['summary']

    with pd.ExcelWriter(
        output,
        engine='xlsxwriter'
    ) as writer:

        assignments.to_excel(
            writer,
            sheet_name='Assignments',
            index=False
        )

        summary.to_excel(
            writer,
            sheet_name='Summary',
            index=False
        )

        for campus in CAMPUSES:

            campus_df = assignments[
                assignments['Campus'] == campus
            ]

            if campus_df.empty:
                continue

            pivot = campus_df.pivot_table(
                index='Role',
                columns='Date',
                values='Person',
                aggfunc='first'
            )

            pivot.to_excel(
                writer,
                sheet_name=campus[:31]
            )

        for sheet in writer.sheets.values():
            sheet.set_zoom(90)
