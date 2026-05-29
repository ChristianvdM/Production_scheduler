def calculate_candidate_score(
    volunteer,
    role,
    campus,
    skill_level,
    metrics,
):

    served_count = metrics[
        "served_counts"
    ][volunteer]

    campus_count = metrics[
        "campus_counts"
    ][volunteer][campus]

    fairness_penalty = (
        served_count * 8
    )

    campus_penalty = (
        campus_count * 2
    )

    proficiency_bonus = (
        skill_level * 15
    )

    score = (
        proficiency_bonus
        - fairness_penalty
        - campus_penalty
    )

    return score
