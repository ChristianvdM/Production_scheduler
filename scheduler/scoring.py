import pandas as pd
import numpy as np

FAIRNESS_WEIGHT = 5
PROFICIENCY_WEIGHT = 2
COVERAGE_WEIGHT = 3
FATIGUE_WEIGHT = 4


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

    def fairness_score(
        self,
        person
    ):

        current = self.assignments_count[person]

        delta = current - self.target_assignments

        return max(
            0,
            100 - (delta * 15)
        )

    def proficiency_score(
        self,
        skill
    ):

        return skill * 25

    def campus_balance_score(
        self,
        person,
        campus
    ):

        counts = self.campus_assignments[person]

        values = list(counts.values())

        if not values:
            return 20

        avg = np.mean(values)

        return max(
            0,
            25 - abs(counts[campus] - avg) * 5
        )

    def fatigue_penalty(
        self,
        person
    ):

        return (
            self.recent_assignments[person] * 20
        )

    def elite_penalty(
        self,
        person
    ):

        person_row = self.skills_matrix.loc[person]

        numeric_values = pd.to_numeric(
            person_row,
            errors="coerce"
        )

        avg_skill = numeric_values.mean()

        if pd.isna(avg_skill):
            avg_skill = 0

        if avg_skill >= 2.5:

            return (
                self.assignments_count[person] * 12
            )

        return 0

    def total_score(
        self,
        person,
        campus,
        skill
    ):

        fairness = self.fairness_score(person)

        proficiency = self.proficiency_score(skill)

        campus_balance = self.campus_balance_score(
            person,
            campus
        )

        fatigue = self.fatigue_penalty(person)

        elite = self.elite_penalty(person)

        return (
            FAIRNESS_WEIGHT * fairness
            + PROFICIENCY_WEIGHT * proficiency
            + COVERAGE_WEIGHT * campus_balance
            - FATIGUE_WEIGHT * fatigue
            - elite
        )
