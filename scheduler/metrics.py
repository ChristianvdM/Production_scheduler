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

    return round(
        (scheduled - cancellations) / scheduled,
        3
    )
