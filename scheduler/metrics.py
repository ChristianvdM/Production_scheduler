from collections import defaultdict


# =========================================================
# BUILD HISTORICAL METRICS
# =========================================================

def build_historical_metrics(
    history
):

    metrics = {

        # =============================================
        # TOTAL SERVES
        # =============================================

        "served_counts":
            defaultdict(int),

        # =============================================
        # CAMPUS SERVES
        # KEY:
        # (volunteer, campus)
        # =============================================

        "campus_counts":
            defaultdict(int),

        # =============================================
        # SUNDAY COUNTS
        # =============================================

        "sunday_counts":
            defaultdict(int)
    }

    # =================================================
    # LOAD HISTORICAL DATA
    # =================================================

    for assignment in history:

        volunteer = (
            assignment.volunteer
        )

        campus = (
            assignment.campus
        )

        service_type = (
            assignment.service_type
        )

        # =============================================
        # TOTAL SERVES
        # =============================================

        metrics["served_counts"][
            volunteer
        ] += 1

        # =============================================
        # CAMPUS SERVES
        # =============================================

        metrics["campus_counts"][
            (
                volunteer,
                campus
            )
        ] += 1

        # =============================================
        # SUNDAY COUNTS
        # =============================================

        if "Sunday" in service_type:

            metrics["sunday_counts"][
                volunteer
            ] += 1

    return metrics
