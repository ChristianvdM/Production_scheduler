import numpy as np
import pandas as pd


def build_metrics(schedule_result):

    assignments = schedule_result.get(
        "assignments",
        pd.DataFrame()
    )

    summary = schedule_result.get(
        "summary",
        pd.DataFrame()
    )

    # -------------------------------------------------
    # EMPTY SAFETY
    # -------------------------------------------------

    if assignments.empty:

        return {
            "coverage_rate": 0,
            "unfilled_roles": 0,
            "fairness_std_dev": 0,
            "avg_skill_score": 0,
            "total_assignments": 0,
            "unique_volunteers": 0,
            "assistant_assignments": 0
        }

    # -------------------------------------------------
    # TOTAL ASSIGNMENTS
    # -------------------------------------------------

    total_assignments = len(assignments)

    # -------------------------------------------------
    # UNIQUE VOLUNTEERS
    # -------------------------------------------------

    unique_volunteers = assignments[
        "Person"
    ].nunique()

    # -------------------------------------------------
    # AVERAGE SKILL SCORE
    # -------------------------------------------------

    if "Skill" in assignments.columns:

        avg_skill_score = round(
            pd.to_numeric(
                assignments["Skill"],
                errors="coerce"
            ).mean(),
            2
        )

    else:

        avg_skill_score = 0

    # -------------------------------------------------
    # FAIRNESS STD DEV
    # -------------------------------------------------

    volunteer_counts = assignments.groupby(
        "Person"
    ).size()

    fairness_std_dev = round(
        np.std(volunteer_counts),
        2
    )

    # -------------------------------------------------
    # ASSISTANT COUNT
    # -------------------------------------------------

    assistant_assignments = len(
        assignments[
            assignments["Role"]
            .astype(str)
            .str.contains(
                "Assistant",
                case=False,
                na=False
            )
        ]
    )

    # -------------------------------------------------
    # COVERAGE RATE
    # -------------------------------------------------

    required_roles_per_campus = 5

    campuses = assignments[
        "Campus"
    ].nunique()

    dates = assignments[
        "Date"
    ].nunique()

    expected_assignments = (
        required_roles_per_campus *
        campuses *
        dates
    )

    if expected_assignments == 0:

        coverage_rate = 0

    else:

        coverage_rate = round(
            (
                total_assignments /
                expected_assignments
            ) * 100,
            1
        )

    # -------------------------------------------------
    # UNFILLED ROLES
    # -------------------------------------------------

    unfilled_roles = max(
        0,
        expected_assignments -
        total_assignments
    )

    # -------------------------------------------------
    # FREE SUNDAY METRIC
    # -------------------------------------------------

    free_sunday_count = 0

    if not summary.empty:

        if "Total Assignments" in summary.columns:

            max_assignments = summary[
                "Total Assignments"
            ].max()

            free_sunday_count = len(
                summary[
                    summary["Total Assignments"]
                    < max_assignments
                ]
            )

    # -------------------------------------------------
    # CAMPUS BALANCE
    # -------------------------------------------------

    campus_balance_score = 0

    campus_columns = [
        c for c in summary.columns
        if c in [
            "Tygerberg",
            "Stellies",
            "Paarl"
        ]
    ]

    if campus_columns:

        campus_totals = summary[
            campus_columns
        ].sum()

        campus_balance_score = round(
            np.std(campus_totals),
            2
        )

    # -------------------------------------------------
    # RETURN METRICS
    # -------------------------------------------------

    return {

        "coverage_rate": coverage_rate,

        "unfilled_roles": int(
            unfilled_roles
        ),

        "fairness_std_dev": fairness_std_dev,

        "avg_skill_score": avg_skill_score,

        "total_assignments": int(
            total_assignments
        ),

        "unique_volunteers": int(
            unique_volunteers
        ),

        "assistant_assignments": int(
            assistant_assignments
        ),

        "free_sunday_count": int(
            free_sunday_count
        ),

        "campus_balance_score": campus_balance_score
    }
