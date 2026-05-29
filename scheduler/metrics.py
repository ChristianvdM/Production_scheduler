from collections import defaultdict


def build_historical_metrics(history):

    metrics = {

        "served_counts":
            defaultdict(int),

        "campus_counts":
            defaultdict(
                lambda: defaultdict(int)
            ),

        "role_counts":
            defaultdict(
                lambda: defaultdict(int)
            ),

        "service_counts":
            defaultdict(
                lambda: defaultdict(int)
            ),
    }

    for item in history:

        metrics["served_counts"][
            item.volunteer
        ] += 1

        metrics["campus_counts"][
            item.volunteer
        ][item.campus] += 1

        metrics["role_counts"][
            item.volunteer
        ][item.role] += 1

        metrics["service_counts"][
            item.volunteer
        ][item.service_type] += 1

    return metrics
