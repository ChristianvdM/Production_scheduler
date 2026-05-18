import pandas as pd
import numpy as np

from collections import defaultdict

from scheduler.scoring import CandidateScorer
from scheduler.repair import repair_schedule

# -------------------------------------------------
# CAMPUSES
# -------------------------------------------------

CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]

# -------------------------------------------------
# SERVICE CONFIGURATION
# -------------------------------------------------

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


# -------------------------------------------------
# SCHEDULER
# -------------------------------------------------

class Scheduler:

    def __init__(
        self,
        skills_df,
        availability_df
    ):

        self.skills_df = skills_df.fillna(0)

        self.availability_df = availability_df.fillna(0)

        self.people = self.skills_df[
            "Name"
        ].tolist()

        self.assignments = []

        self.logs = []

        self.schedule = defaultdict(dict)

        # -----------------------------------------
        # TRACKING
        # -----------------------------------------

        self.assignments_count = defaultdict(int)

        self.assistant_assignments = defaultdict(int)

        self.campus_assignments = defaultdict(
            lambda: defaultdict(int)
        )

        self.recent_assignments = defaultdict(int)

        self.sundays_worked = defaultdict(set)

        # -----------------------------------------
        # DATE COLUMNS
        # -----------------------------------------

        self.date_columns = [

            c for c in self.availability_df.columns

            if c != "Name"
        ]

        # -----------------------------------------
        # SKILLS MATRIX
        # -----------------------------------------

        self.skills_matrix = self.build_skill_matrix()

        # -----------------------------------------
        # TARGET ASSIGNMENTS
        # -----------------------------------------

        self.target_assignments = (
            self.calculate_target_assignments()
        )

        # -----------------------------------------
        # SCORER
        # -----------------------------------------

        self.scorer = CandidateScorer(
            self.assignments_count,
            self.campus_assignments,
            self.recent_assignments,
            self.target_assignments,
            self.skills_matrix
        )

    # -------------------------------------------------
    # LOGGER
    # -------------------------------------------------

    def log(self, message):

        print(message)

        self.logs.append(message)

    # -------------------------------------------------
    # SKILL MATRIX
    # -------------------------------------------------

    def build_skill_matrix(self):

        df = self.skills_df.copy()

        return df.set_index("Name")

    # -------------------------------------------------
    # TARGET ASSIGNMENTS
    # -------------------------------------------------

    def calculate_target_assignments(self):

        total_dates = len(self.date_columns)

        roles_per_service = 5

        total_slots = (
            total_dates *
            len(CAMPUSES) *
            roles_per_service
        )

        people_count = max(
            1,
            len(self.people)
        )

        return max(
            1,
            round(total_slots / people_count)
        )

    # -------------------------------------------------
    # AVAILABLE PEOPLE
    # -------------------------------------------------

    def available_people(self, date):

        if date not in self.availability_df.columns:
            return []

        rows = self.availability_df[

            self.availability_df[date]
            .astype(str)
            .str.lower()
            .isin([
                "yes",
                "y",
                "available",
                "1",
                "true"
            ])
        ]

        return rows["Name"].tolist()

    # -------------------------------------------------
    # GET SKILL
    # -------------------------------------------------

    def get_skill(
        self,
        person,
        role,
        campus
    ):

        col = f"{role}_{campus}"

        if col not in self.skills_matrix.columns:
            return 0

        try:

            value = self.skills_matrix.loc[
                person,
                col
            ]

            return float(value)

        except:

            return 0

    # -------------------------------------------------
    # ASSISTANT ELIGIBILITY
    # -------------------------------------------------

    def eligible_assistant(
        self,
        person,
        role,
        campus
    ):

        base_role = role.replace(
            " Assistant",
            ""
        )

        skill = self.get_skill(
            person,
            base_role,
            campus
        )

        return 0 < skill < 2

    # -------------------------------------------------
    # RUNNER ELIGIBILITY
    # -------------------------------------------------

    def eligible_runner(
        self,
        person,
        campus
    ):

        level_one_count = 0

        for role in [
            "Sound",
            "Lights",
            "Resi"
        ]:

            skill = self.get_skill(
                person,
                role,
                campus
            )

            if skill == 1:
                level_one_count += 1

        return level_one_count >= 2

    # -------------------------------------------------
    # ASSIGN ROLE
    # -------------------------------------------------

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

        available = self.available_people(
            date
        )

        candidates = []

        for person in available:

            if person in used_people:
                continue

            # -------------------------------------
            # MAIN / DIRECTOR
            # -------------------------------------

            if role_type in [
                "director",
                "main"
            ]:

                skill = self.get_skill(
                    person,
                    role,
                    campus
                )

                if skill < role_config[
                    "min_skill"
                ]:
                    continue

            # -------------------------------------
            # ASSISTANT
            # -------------------------------------

            elif role_type == "assistant":

                if not self.eligible_assistant(
                    person,
                    role,
                    campus
                ):
                    continue

                skill = 1

            # -------------------------------------
            # RUNNER
            # -------------------------------------

            elif role_type == "runner":

                if not self.eligible_runner(
                    person,
                    campus
                ):
                    continue

                skill = 1

            else:
                continue

            # -------------------------------------
            # SCORE
            # -------------------------------------

            score = self.scorer.total_score(
                person,
                campus,
                skill
            )

            # -------------------------------------
            # ASSISTANT FAIRNESS
            # -------------------------------------

            if role_type == "assistant":

                score -= (
                    self.assistant_assignments[
                        person
                    ] * 30
                )

            # -------------------------------------
            # FREE SUNDAY PREFERENCE
            # -------------------------------------

            if service_type == "Sunday":

                if len(
                    self.sundays_worked[
                        person
                    ]
                ) >= 3:

                    score -= 15

            candidates.append(
                (
                    score,
                    person,
                    skill
                )
            )

        # -----------------------------------------
        # NO CANDIDATES
        # -----------------------------------------

        if not candidates:

            self.log(
                f"WARNING: No candidates "
                f"for {role} "
                f"at {campus} "
                f"on {date}"
            )

            return

        # -----------------------------------------
        # PICK BEST
        # -----------------------------------------

        candidates = sorted(
            candidates,
            key=lambda x: x[0],
            reverse=True
        )

        best_score, best_person, best_skill = (
            candidates[0]
        )

        # -----------------------------------------
        # UPDATE TRACKING
        # -----------------------------------------

        used_people.add(best_person)

        self.assignments_count[
            best_person
        ] += 1

        self.campus_assignments[
            best_person
        ][campus] += 1

        if role_type == "assistant":

            self.assistant_assignments[
                best_person
            ] += 1

        if service_type == "Sunday":

            self.sundays_worked[
                best_person
            ].add(date)

        # -----------------------------------------
        # STORE ASSIGNMENT
        # -----------------------------------------

        self.schedule[
            (date, campus)
        ][role] = best_person

        self.assignments.append({

            "Date": date,

            "Campus": campus,

            "Service": service_type,

            "Role": role,

            "Person": best_person,

            "Skill": best_skill,

            "Score": round(best_score, 2)
        })

        # -----------------------------------------
        # LOG SUCCESS
        # -----------------------------------------

        self.log(
            f"Assigned {best_person} "
            f"to {role} "
            f"at {campus} "
            f"on {date}"
        )

    # -------------------------------------------------
    # GENERATE SCHEDULE
    # -------------------------------------------------

    def generate(
        self,
        progress_callback=None
    ):

        self.log(
            "Starting schedule generation..."
        )

        total_steps = (
            len(self.date_columns) *
            len(CAMPUSES) *
            3
        )

        current_step = 0

        for date in self.date_columns:

            self.log(
                f"Processing date: {date}"
            )

            service_type = "Sunday"

            for campus in CAMPUSES:

                self.log(
                    f"Scheduling campus: {campus}"
                )

                used_people = set()

                # ---------------------------------
                # PASS 1 — DIRECTORS
                # ---------------------------------

                current_step += 1

                if progress_callback:

                    progress_callback(
                        current_step / total_steps,
                        f"{date} | {campus} | Directors"
                    )

                self.log(
                    f"{date} | {campus} | PASS 1 Directors"
                )

                for role_config in SERVICE_CONFIG[
                    service_type
                ]:

                    if role_config[
                        "type"
                    ] != "director":
                        continue

                    for _ in range(
                        role_config["count"]
                    ):

                        self.assign_role(
                            date,
                            campus,
                            role_config,
                            used_people,
                            service_type
                        )

                # ---------------------------------
                # PASS 2 — MAIN
                # ---------------------------------

                current_step += 1

                if progress_callback:

                    progress_callback(
                        current_step / total_steps,
                        f"{date} | {campus} | Main Roles"
                    )

                self.log(
                    f"{date} | {campus} | PASS 2 Main Roles"
                )

                for role_config in SERVICE_CONFIG[
                    service_type
                ]:

                    if role_config[
                        "type"
                    ] != "main":
                        continue

                    for _ in range(
                        role_config["count"]
                    ):

                        self.assign_role(
                            date,
                            campus,
                            role_config,
                            used_people,
                            service_type
                        )

                # ---------------------------------
                # PASS 3 — ASSISTANTS
                # ---------------------------------

                current_step += 1

                if progress_callback:

                    progress_callback(
                        current_step / total_steps,
                        f"{date} | {campus} | Assistants"
                    )

                self.log(
                    f"{date} | {campus} | PASS 3 Assistants"
                )

                for role_config in SERVICE_CONFIG[
                    service_type
                ]:

                    if role_config[
                        "type"
                    ] != "assistant":
                        continue

                    for _ in range(
                        role_config["count"]
                    ):

                        self.assign_role(
                            date,
                            campus,
                            role_config,
                            used_people,
                            service_type
                        )

        # -----------------------------------------
        # REPAIR PASS
        # -----------------------------------------

        self.log(
            "Starting repair pass..."
        )

        repair_schedule(
            self.schedule,
            self.skills_df,
            self.availability_df,
            self.assignments
        )

        self.log(
            "Repair pass complete."
        )

        return self.build_result()

    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------

    def build_summary(self):

        summary = pd.DataFrame(
            self.assignments
        )

        if summary.empty:
            return pd.DataFrame()

        totals = summary.groupby(
            "Person"
        ).size().reset_index(
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

        result["Target Assignments"] = (
            self.target_assignments
        )

        result["Fairness Delta"] = (
            result["Total Assignments"] -
            result["Target Assignments"]
        )

        return result.sort_values(
            by="Total Assignments",
            ascending=False
        )

    # -------------------------------------------------
    # BUILD RESULT
    # -------------------------------------------------

    def build_result(self):

        assignments_df = pd.DataFrame(
            self.assignments
        )

        summary_df = self.build_summary()

        return {

            "assignments": assignments_df,

            "summary": summary_df,

            "schedule": self.schedule,

            "target_assignments":
                self.target_assignments,

            "logs": self.logs
        }


# -------------------------------------------------
# EXTERNAL GENERATOR
# -------------------------------------------------

def generate_schedule(
    skills_df,
    availability_df,
    progress_callback=None
):

    scheduler = Scheduler(
        skills_df,
        availability_df
    )

    return scheduler.generate(
        progress_callback=progress_callback
    )
