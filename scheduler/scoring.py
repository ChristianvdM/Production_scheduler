import pandas as pd
import numpy as np

FAIRNESS_WEIGHT = 5
PROFICIENCY_WEIGHT = 2
COVERAGE_WEIGHT = 3
FATIGUE_WEIGHT = 4
ELITE_PENALTY_WEIGHT = 12
FREE_SUNDAY_WEIGHT = 15


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

    def elite_penalty(self, person):

    try:

        numeric_values = pd.to_numeric(
            self.skills_matrix.loc[person],
            errors="coerce"
        )

        avg_skill = numeric_values.mean()

        if pd.isna(avg_skill):
            return 0

        if avg_skill >= 2.5:

            return (
                self.assignments_count[person]
                * ELITE_PENALTY_WEIGHT
            )

    except:
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

        if 0 < skill < 2:
            return 15

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
