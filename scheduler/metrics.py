from collections import defaultdict


def build_historical_metrics(history):

    metrics = {
        "served_counts": defaultdict(int),
        "campus_counts": defaultdict(lambda: defaultdict(int)),
        "role_counts": defaultdict(lambda: defaultdict(int)),
        "service_counts": defaultdict(lambda: defaultdict(int)),
        "scheduled_counts": defaultdict(int),
        "cancellations": defaultdict(int),
    }

    for item in history:

        metrics["scheduled_counts"][item.volunteer] += 1

        if item.served:

            metrics["served_counts"][item.volunteer] += 1

            metrics["campus_counts"][item.volunteer][item.campus] += 1

            metrics["role_counts"][item.volunteer][item.role] += 1

            metrics["service_counts"][item.volunteer][item.service_type] += 1

        else:
            metrics["cancellations"][item.volunteer] += 1

    return metrics


def get_reliability_score(metrics, volunteer):

    scheduled = metrics["scheduled_counts"][volunteer]

    if scheduled == 0:
        return 1.0

    cancellations = metrics["cancellations"][volunteer]

    return round((scheduled - cancellations) / scheduled, 3)import pandas as pd

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
