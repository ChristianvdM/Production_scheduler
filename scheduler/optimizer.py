import pandas as pd
import numpy as np

from collections import defaultdict

from scheduler.scoring import CandidateScorer
from scheduler.repair import repair_schedule

CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]

SERVICE_CONFIG = {
    "Sunday": [
        {
            "role": "Director",
            "type": "director",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Sound",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Lights",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Resi",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Sound Assistant",
            "type": "assistant",
            "min_skill": 0.1,
            "max_skill": 1.99,
            "count": 1
        }
    ],

    "Prayer": [
        {
            "role": "Sound",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Sound Assistant",
            "type": "assistant",
            "min_skill": 0.1,
            "max_skill": 1.99,
            "count": 2
        },

        {
            "role": "Runner",
            "type": "runner",
            "count": 1
        }
    ]
}


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

        self.assistant_assignments = defaultdict(int)

        self.campus_assignments = defaultdict(
            lambda: defaultdict(int)
        )

        self.recent_assignments = defaultdict(int)

        self.sundays_worked = defaultdict(set)

        self.schedule = defaultdict(dict)

        self.date_columns = [
            c for c in availability_df.columns
            if c != "Name"
        ]

        self.skills_matrix = self.build_skill_matrix()

        self.target_assignments = self.calculate_target_assignments()

        self.scorer = CandidateScorer(
            self.assignments_count,
            self.campus_assignments,
            self.recent_assignments,
            self.target_assignments,
            self.skills_matrix
        )

    def build_skill_matrix(self):

        df = self.skills_df.copy()

        return df.set_index("Name")

    def calculate_target_assignments(self):

        total_dates = len(self.date_columns)

        estimated_roles_per_date = len(CAMPUSES) * 5

        total_slots = total_dates * estimated_roles_per_date

        return max(
            1,
            total_slots // max(1, len(self.people))
        )

    def available_people(self, date):

        rows = self.availability_df[
            self.availability_df[date].astype(str).str.lower().isin([
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

        col = f"{role}_{campus}"

        if col not in self.skills_df.columns:
            return 0

        try:
            value = self.skills_matrix.loc[person, col]
            return float(value)

        except:
            return 0

    def eligible_runner(
        self,
        person,
        campus
    ):

        level_one_count = 0

        for role in ["Sound", "Lights", "Resi"]:

            col = f"{role}_{campus}"

            if col not in self.skills_df.columns:
                continue

            try:
                skill = float(
                    self.skills_matrix.loc[person, col]
                )

                if skill == 1:
                    level_one_count += 1

            except:
                pass

        return level_one_count >= 2

    def eligible_assistant(
        self,
        person,
        role,
        campus
    ):

        base_role = role.replace(" Assistant", "")

        skill = self.get_skill(
            person,
            base_role,
            campus
        )

        return 0 < skill < 2

    def assign_role(
        self,
        date,
        campus,
        role_config,
        used_people,
        service_type
    ):

        role = role_config["role"]

        role_type = role_config["type"]

        available = self.available_people(date)

        candidates = []

        for person in available:

            if person in used_people:
                continue

            if role_type in ["director", "main"]:

                skill = self.get_skill(
                    person,
                    role,
                    campus
                )

                if skill < role_config["min_skill"]:
                    continue

            elif role_type == "assistant":

                if not self.eligible_assistant(
                    person,
                    role,
                    campus
                ):
                    continue

                skill = 1

            elif role_type == "runner":

                if not self.eligible_runner(
                    person,
                    campus
                ):
                    continue

                skill = 1

            else:
                continue

            score = self.scorer.total_score(
                person,
                campus,
                skill
            )

            if role_type == "assistant":

                score -= (
                    self.assistant_assignments[person] * 30
                )

            if service_type == "Sunday":

                if len(self.sundays_worked[person]) >= 3:
                    score -= 15

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

        if service_type == "Sunday":
            self.sundays_worked[best_person].add(date)

        if role_type == "assistant":
            self.assistant_assignments[best_person] += 1

        self.schedule[(date, campus)][role] = best_person

        self.assignments.append(
            {
                "Date": date,
                "Campus": campus,
                "Service": service_type,
                "Role": role,
                "Person": best_person,
                "Skill": best_skill,
                "Score": best_score
            }
        )

    def generate(self):

        for date in self.date_columns:

            service_type = "Sunday"

            for campus in CAMPUSES:

                used_people = set()

                # PASS 1 — DIRECTORS
                for role_config in SERVICE_CONFIG[service_type]:

                    if role_config["type"] != "director":
                        continue

                    for _ in range(role_config["count"]):

                        self.assign_role(
                            date,
                            campus,
                            role_config,
                            used_people,
                            service_type
                        )

                # PASS 2 — MAIN
                for role_config in SERVICE_CONFIG[service_type]:

                    if role_config["type"] != "main":
                        continue

                    for _ in range(role_config["count"]):

                        self.assign_role(
                            date,
                            campus,
                            role_config,
                            used_people,
                            service_type
                        )

                # PASS 3 — ASSISTANTS
                for role_config in SERVICE_CONFIG[service_type]:

                    if role_config["type"] != "assistant":
                        continue

                    for _ in range(role_config["count"]):

                        self.assign_role(
                            date,
                            campus,
                            role_config,
                            used_people,
                            service_type
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

        totals = summary.groupby("Person").size().reset_index(
            name="Total Assignments"
        )

        campus_breakdown = summary.pivot_table(
            index="Person",
            columns="Campus",
            values="Role",
            aggfunc="count",
            fill_value=0
        ).reset_index()

        result = totals.merge(
            campus_breakdown,
            on="Person",
            how="left"
        )

        result["Target Assignments"] = self.target_assignments

        result["Fairness Delta"] = (
            result["Total Assignments"] -
            result["Target Assignments"]
        )

        return result.sort_values(
            by="Total Assignments",
            ascending=False
        )

    def build_result(self):

        assignments_df = pd.DataFrame(self.assignments)

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
