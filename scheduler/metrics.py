import numpy as np


def build_metrics(schedule_result):

    assignments = schedule_result['assignments']

    if assignments.empty:

        return {
            "coverage_rate": 0,
            "unfilled_roles": 0,
            "fairness_std_dev": 0,
            "avg_skill_score": 0
        }

    role_count = len(assignments)

    avg_skill = round(
        assignments['Skill'].mean(),
        2
    )

    volunteer_counts = assignments.groupby(
        'Person'
    ).size()

    fairness_std = round(
        np.std(volunteer_counts),
        2
    )

    return {
        "coverage_rate": 100,
        "unfilled_roles": 0,
        "fairness_std_dev": fairness_std,
        "avg_skill_score": avg_skill
    }
