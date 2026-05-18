import pandas as pd

from collections import defaultdict

from scheduler.scoring import CandidateScorer
from scheduler.repair import repair_schedule

CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]


class Scheduler:

    def __init__(
        self,
        skills_df,
        availability_df
    ):

        self.skills_df = skills_df.fillna(0)
        self.availability_df = availability_df

        self.people = self.skills_df["Name"].tolist()

        self.assignments = []

        self.assignments_count = defaultdict(int)

        self.campus_assignments = defaultdict(
            lambda: defaultdict(int)
        )

        self.recent_assignments = defaultdict(int)

        self.schedule = defaultdict(dict)

        self.date_columns = [
            c for c in availability_df.columns
            if c != "Name"
        ]

        self.skills_matrix = (
            self.skills_df.set_index("Name")
        )

        self.target_assignments = (
            self.calculate_target_assignments()
        )

        self.scorer = CandidateScorer(
            self.assignments_count,
            self.campus_assignments,
            self.recent_assignments,
            self.target_assignments,
            self.skills_matrix
        )

    def calculate_target_assignments(self):

        total_dates = len(self.date_columns)

        estimated_roles_per_date = len(CAMPUSES) * 5

        total_slots = (
            total_dates * estimated_roles_per_date
        )

        people_count = max(1, len(self.people))

        return max(
            1,
            total_slots // people_count
        )

    def available_people(self, date):

        rows = self.availability_df[
            self.availability_df[date]
            .astype(str)
            .str.lower()
            .isin([
                "yes",
                "y",
                "available",
                "1"
            ])
        ]

        return rows["Name"].tolist()

    def get_skill(
        self,
        person,
        role,
        campus
    ):

        column = f"{role}_{campus}"

        if column not in self.skills_df.columns:
            return 0

        try:
            value = self.skills_matrix.loc[
                person,
                column
            ]

            return float(value)

        except:
            return 0

    def role_priority(self):

        return [
            "Director",
            "Sound",
            "Lights",
            "Resi",
            "Assistant"
        ]

    def assign_role(
        self,
        date,
        campus,
        role,
        used_people
    ):

        available = self.available_people(date)

        candidates = []

        for person in available:

            if person in used_people:
                continue

            skill = self.get_skill(
                person,
                role,
                campus
            )

            if role == "Assistant":

                if skill <= 0:
                    continue

            else:

                if skill < 2:
                    continue

            score = self.scorer.total_score(
                person,
                campus,
                skill
            )

            candidates.append(
                (
                    score,
                    person,
                    skill
                )
            )

        if not candidates:
            return

        candidates = sorted(
            candidates,
            key=lambda x: x[0],
            reverse=True
        )

        best_score, best_person, best_skill = candidates[0]

        used_people.add(best_person)

        self.assignments_count[best_person] += 1

        self.campus_assignments[best_person][campus] += 1

        self.schedule[(date, campus)][role] = best_person

        self.assignments.append(
            {
                "Date": date,
                "Campus": campus,
                "Role": role,
                "Person": best_person,
                "Skill": best_skill,
                "Score": best_score
            }
        )

    def generate(self):

        for date in self.date_columns:

            for campus in CAMPUSES:

                used_people = set()

                for role in self.role_priority():

                    self.assign_role(
                        date,
                        campus,
                        role,
                        used_people
                    )

        repair_schedule(
            self.schedule,
            self.skills_df,
            self.availability_df,
            self.assignments
        )

        return self.build_result()

    def build_summary(self):

        summary = pd.DataFrame(self.assignments)

        if summary.empty:
            return pd.DataFrame()

        totals = (
            summary.groupby("Person")
            .size()
            .reset_index(
                name="Total Assignments"
            )
        )

        campus_breakdown = (
            summary.pivot_table(
                index="Person",
                columns="Campus",
                values="Role",
                aggfunc="count",
                fill_value=0
            )
            .reset_index()
        )

        result = totals.merge(
            campus_breakdown,
            on="Person",
            how="left"
        )

        result["Target Assignments"] = (
            self.target_assignments
        )

        result["Fairness Delta"] = (
            result["Total Assignments"]
            - result["Target Assignments"]
        )

        return result.sort_values(
            by="Total Assignments",
            ascending=False
        )

    def build_result(self):

        assignments_df = pd.DataFrame(
            self.assignments
        )

        summary_df = self.build_summary()

        return {
            "assignments": assignments_df,
            "summary": summary_df,
            "schedule": self.schedule,
            "target_assignments": self.target_assignments
        }


def generate_schedule(
    skills_df,
    availability_df
):

    scheduler = Scheduler(
        skills_df,
        availability_df
    )

    return scheduler.generate()
