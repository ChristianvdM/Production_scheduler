# =========================================================
# CANDIDATE SCORE
# =========================================================

def calculate_candidate_score(

    volunteer,

    role,

    campus,

    skill_level,

    metrics
):

    served_counts = metrics[
        "served_counts"
    ]

    campus_counts = metrics[
        "campus_counts"
    ]

    total_served = served_counts.get(
        volunteer,
        0
    )

    campus_served = campus_counts.get(
        (volunteer, campus),
        0
    )

    # =====================================================
    # PRIORITY 1:
    # ROLE COVERAGE
    # =====================================================

    coverage_weight = 1000

    # =====================================================
    # PRIORITY 2:
    # FAIRNESS
    # =====================================================

    fairness_penalty = (
        total_served * 15
    )

    campus_penalty = (
        campus_served * 8
    )

    # =====================================================
    # PRIORITY 3:
    # SKILL
    # =====================================================

    skill_bonus = (
        skill_level * 10
    )

    # =====================================================
    # FINAL SCORE
    # =====================================================

    score = (

        coverage_weight

        + skill_bonus

        - fairness_penalty

        - campus_penalty
    )

    return score
