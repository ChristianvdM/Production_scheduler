import pandas as pd
import numpy as np

# -------------------------------------------------
# WEIGHTING CONFIGURATION
# -------------------------------------------------

FAIRNESS_WEIGHT = 5

PROFICIENCY_WEIGHT = 2

COVERAGE_WEIGHT = 3

FATIGUE_WEIGHT = 4

ELITE_PENALTY_WEIGHT = 12

FREE_SUNDAY_WEIGHT = 15

LOW_SKILL_BONUS = 15


# -------------------------------------------------
# CANDIDATE SCORER
# -------------------------------------------------

class CandidateScorer:

    def __init__(
        self,
        assignments_count,
        campus_assignments,
        recent_assignments,
        target_assignments,
        skills_matrix
    ):

        self.assignments_count = assignments_count

        self.campus_assignments = campus_assignments

        self.recent_assignments = recent_assignments

        self.target_assignments = target_assignments

        self.skills_matrix = skills_matrix

    # -------------------------------------------------
    # FAIRNESS SCORE
    # -------------------------------------------------

    def fairness_score(
        self,
        person
    ):

        current_assignments = (
            self.assignments_count[person]
        )

        delta = (
            current_assignments -
            self.target_assignments
        )

        return max(
            0,
            100 - (delta * 15)
        )

    # -------------------------------------------------
    # PROFICIENCY SCORE
    # -------------------------------------------------

    def proficiency_score(
        self,
        skill
    ):

        return skill * 25

    # -------------------------------------------------
    # CAMPUS BALANCE SCORE
    # -------------------------------------------------

    def campus_balance_score(
        self,
        person,
        campus
    ):

        counts = self.campus_assignments[
            person
        ]

        values = list(
            counts.values()
        )

        if not values:
            return 20

        avg = np.mean(values)

        return max(
            0,
            25 - abs(
                counts[campus] - avg
            ) * 5
        )

    # -------------------------------------------------
    # FATIGUE PENALTY
    # -------------------------------------------------

    def fatigue_penalty(
        self,
        person
    ):

        return (
            self.recent_assignments[person]
            * 20
        )

    # -------------------------------------------------
    # ELITE PENALTY
    # -------------------------------------------------

    def elite_penalty(
        self,
        person
    ):

        """
        Prevent overusing highly skilled people.
        Handles mixed string/numeric rows safely.
        """

        try:

            row = self.skills_matrix.loc[
                person
            ]

            numeric_values = pd.to_numeric(
                row,
                errors="coerce"
            )

            numeric_values = numeric_values.dropna()

            if numeric_values.empty:
                return 0

            avg_skill = numeric_values.mean()

            if avg_skill >= 2.5:

                return (
                    self.assignments_count[
                        person
                    ] *
                    ELITE_PENALTY_WEIGHT
                )

        except Exception:

            return 0

        return 0

    # -------------------------------------------------
    # FREE SUNDAY PENALTY
    # -------------------------------------------------

    def free_sunday_penalty(
        self,
        sundays_worked
    ):

        if sundays_worked >= 3:

            return FREE_SUNDAY_WEIGHT

        return 0

    # -------------------------------------------------
    # LOW SKILL BONUS
    # -------------------------------------------------

    def low_skill_bonus(
        self,
        skill
    ):

        """
        Encourages low proficiency volunteers
        to get exposure.
        """

        if 0 < skill < 2:

            return LOW_SKILL_BONUS

        return 0

    # -------------------------------------------------
    # TOTAL SCORE
    # -------------------------------------------------

    def total_score(
        self,
        person,
        campus,
        skill
    ):

        fairness = self.fairness_score(
            person
        )

        proficiency = self.proficiency_score(
            skill
        )

        campus_balance = (
            self.campus_balance_score(
                person,
                campus
            )
        )

        fatigue = self.fatigue_penalty(
            person
        )

        elite = self.elite_penalty(
            person
        )

        low_skill = self.low_skill_bonus(
            skill
        )

        total = (

            FAIRNESS_WEIGHT * fairness +

            PROFICIENCY_WEIGHT * proficiency +

            COVERAGE_WEIGHT * campus_balance +

            low_skill -

            FATIGUE_WEIGHT * fatigue -

            elite
        )

        return round(total, 2)
