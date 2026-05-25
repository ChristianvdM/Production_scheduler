import pandas as pd

from scheduler.optimizer import (
    CAMPUSES,
    SERVICE_CONFIG
)

# -------------------------------------------------
# BUILD METRICS
# -------------------------------------------------

def build_metrics(
    schedule_result
):

    assignments = schedule_result[
        "assignments"
    ]

    summary = schedule_result[
        "summary"
    ]

    if assignments.empty:

        return {

            "coverage_rate": 0,

            "unfilled_roles": 0,

            "fairness_std_dev": 0,

            "avg_skill_score": 0
        }

    # =============================================
    # EXPECTED ROLE COUNT
    # =============================================

    expected_roles = 0

    unique_dates = assignments[[
        "Date",
        "Service"
    ]].drop_duplicates()

    for _, row in unique_dates.iterrows():

        service = row["Service"]

        roles = SERVICE_CONFIG[
            service
        ]

        role_count = sum(
            r["count"]
            for r in roles
        )

        # -----------------------------------------
        # PRAYER
        # -----------------------------------------

        if service == "Prayer":

            expected_roles += role_count

        # -----------------------------------------
        # SUNDAY SERVICES
        # -----------------------------------------

        else:

            expected_roles += (
                role_count *
                len(CAMPUSES)
            )

    # =============================================
    # ACTUAL ASSIGNMENTS
    # =============================================

    actual_roles = len(assignments)

    # =============================================
    # COVERAGE
    # =============================================

    if expected_roles == 0:

        coverage_rate = 0

    else:

        coverage_rate = round(

            (
                actual_roles /
                expected_roles
            ) * 100,

            1
        )

    unfilled_roles = max(
        0,
        expected_roles - actual_roles
    )

    # =============================================
    # FAIRNESS
    # =============================================

    if summary.empty:

        fairness_std_dev = 0

    else:

        fairness_std_dev = round(

            summary[
                "Total Assignments"
            ].std(),

            2
        )

        if pd.isna(
            fairness_std_dev
        ):

            fairness_std_dev = 0

    # =============================================
    # SKILL SCORE
    # =============================================

    avg_skill_score = round(

        assignments[
            "Skill"
        ].mean(),

        2
    )

    if pd.isna(
        avg_skill_score
    ):

        avg_skill_score = 0

    # =============================================
    # RETURN
    # =============================================

    return {

        "coverage_rate":
            coverage_rate,

        "unfilled_roles":
            unfilled_roles,

        "fairness_std_dev":
            fairness_std_dev,

        "avg_skill_score":
            avg_skill_score
    }
