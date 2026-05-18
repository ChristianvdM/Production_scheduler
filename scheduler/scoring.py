import numpy as np
        current = self.assignments_count[person]

        delta = current - self.target_assignments

        return max(0, 100 - (delta * 15))

    def proficiency_score(self, skill):

        return skill * 25

    def campus_balance_score(self, person, campus):

        counts = self.campus_assignments[person]

        values = list(counts.values())

        if not values:
            return 20

        avg = np.mean(values)

        return max(0, 25 - abs(counts[campus] - avg) * 5)

    def fatigue_penalty(self, person):

        return self.recent_assignments[person] * 20

    def elite_penalty(self, person):

        avg_skill = self.skills_matrix.loc[person].mean()

        if avg_skill >= 2.5:
            return self.assignments_count[person] * 12

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
            FAIRNESS_WEIGHT * fairness +
            PROFICIENCY_WEIGHT * proficiency +
            COVERAGE_WEIGHT * campus_balance -
            FATIGUE_WEIGHT * fatigue -
            elite
        )
