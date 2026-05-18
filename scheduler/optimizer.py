import pandas as pd
import re

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
        # DIRECTOR ROTATION TRACKING
        # -----------------------------------------

        self.director_campus_history = defaultdict(
            lambda: defaultdict(int)
        )

        self.last_director_campus = {}

        # -----------------------------------------
        # SPOUSE / FAMILY DETECTION
        # -----------------------------------------

        self.family_groups = defaultdict(list)

        for person in self.people:

            parts = str(person).strip().split()

            if len(parts) < 2:
                continue

            surname = parts[-1].lower()

            self.family_groups[
                surname
            ].append(person)

        # -----------------------------------------
        # DATE COLUMNS + SERVICE TYPES
        # -----------------------------------------

        self.date_columns = []

        self.service_map = {}

        self.original_column_map = {}

        pattern = re.compile(
            r"^(\d{1,2}\s+[A-Za-z]+)\s*-\s*(Prayer|Services)$"
        )

        for c in self.availability_df.columns:

            if c == "Name":
                continue

            column = str(c).strip()

            match = pattern.match(column)

            if not match:
                continue

            extracted_date = match.group(1).strip()

            extracted_service = match.group(2).strip()

            if extracted_date not in self.date_columns:

                self.date_columns.append(
                    extracted_date
                )

            if extracted_service == "Services":

                self.service_map[
                    extracted_date
                ] = "Sunday"

            else:

                self.service_map[
                    extracted_date
                ] = "Prayer"

            self.original_column_map[
                extracted_date
            ] = column

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
    # SKILL MATRIX
    # -------------------------------------------------

    def build_skill_matrix(self):

        df = self.skills_df.copy()

        return df.set_index("Name")

    # -------------------------------------------------
    # TARGET ASSIGNMENTS
    # -------------------------------------------------

    def calculate_target_assignments(self):

        total_slots = 0

        for date in self.date_columns:

            service_type = self.service_map.get(
                date,
                "Sunday"
            )

            roles = SERVICE_CONFIG[
                service_type
            ]

            role_count = sum(
                r["count"]
                for r in roles
            )

            if service_type == "Prayer":

                total_slots += role_count

            else:

                total_slots += (
                    role_count *
                    len(CAMPUSES)
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

        original_column = (
            self.original_column_map.get(date)
        )

        if not original_column:
            return []

        if original_column not in self.availability_df.columns:
            return []

        rows = self.availability_df[

            self.availability_df[
                original_column
            ]
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

        # -----------------------------------------
        # PRAYER NIGHT
        # -----------------------------------------

        if campus == "Prayer":

            if role == "Runner":
                return 1

            if role == "Director":

                if "Director" not in self.skills_matrix.columns:
                    return 0

                try:

                    value = self.skills_matrix.loc[
                        person,
                        "Director"
                    ]

                    return float(value)

                except:

                    return 0

            if role == "Sound Assistant":

                role = "Sound"

            prayer_cols = [

                c for c in self.skills_matrix.columns

                if c.startswith("Sound_")
            ]

            if not prayer_cols:
                return 0

            values = []

            for col in prayer_cols:

                try:

                    values.append(
                        float(
                            self.skills_matrix.loc[
                                person,
                                col
                            ]
                        )
                    )

                except:
                    continue

            if not values:
                return 0

            return max(values)

        # -----------------------------------------
        # DIRECTOR SPECIAL CASE
        # -----------------------------------------

        if role == "Director":

            if "Director" not in self.skills_matrix.columns:
                return 0

            try:

                value = self.skills_matrix.loc[
                    person,
                    "Director"
                ]

                return float(value)

            except:

                return 0

        # -----------------------------------------
        # NORMAL CAMPUS ROLES
        # -----------------------------------------

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
    # FAMILY CAMPUS MATCHING
    # -------------------------------------------------

    def family_same_campus_bonus(
        self,
        person,
        campus,
        date
    ):

        parts = str(person).strip().split()

        if len(parts) < 2:
            return 0

        surname = parts[-1].lower()

        family_members = self.family_groups.get(
            surname,
            []
        )

        if len(family_members) <= 1:
            return 0

        bonus = 0

        for assignment in self.assignments:

            if assignment["Date"] != date:
                continue

            if assignment["Campus"] != campus:
                continue

            assigned_person = assignment["Person"]

            if assigned_person == person:
                continue

            assigned_parts = str(
                assigned_person
            ).strip().split()

            if len(assigned_parts) < 2:
                continue

            assigned_surname = (
                assigned_parts[-1].lower()
            )

            if assigned_surname == surname:

                bonus += 75

        return bonus

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

            # -------------------------------------
            # GLOBAL DAILY LOCK
            # -------------------------------------

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
            # FAMILY CAMPUS MATCHING
            # -------------------------------------

            if service_type == "Sunday":

                score += self.family_same_campus_bonus(
                    person,
                    campus,
                    date
                )

            # -------------------------------------
            # DIRECTOR ROTATION
            # -------------------------------------

            if role == "Director":

                score -= (

                    self.director_campus_history[
                        person
                    ][campus] * 25
                )

                last_assignment = (
                    self.last_director_campus.get(
                        person
                    )
                )

                if last_assignment:

                    last_campus = last_assignment[
                        "campus"
                    ]

                    if last_campus == campus:

                        score -= 1000

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
        # TRACK DIRECTOR ROTATION
        # -----------------------------------------

        if role == "Director":

            self.director_campus_history[
                best_person
            ][campus] += 1

            self.last_director_campus[
                best_person
            ] = {

                "date": date,

                "campus": campus
            }

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

            "Skill": best_skill
        })

    # -------------------------------------------------
    # GENERATE SCHEDULE
    # -------------------------------------------------

    def generate(
        self,
        progress_callback=None
    ):

        total_steps = (
            len(self.date_columns) * 3
        )

        current_step = 0

        for date in self.date_columns:

            service_type = self.service_map.get(
                date,
                "Sunday"
            )

            # =====================================
            # GLOBAL DAILY LOCK
            # =====================================

            daily_used_people = set()

            # =====================================
            # PRAYER NIGHT
            # =====================================

            if service_type == "Prayer":

                campus = "Prayer"

                current_step += 1

                if progress_callback:

                    progress_callback(
                        current_step / total_steps,
                        f"{date} | Prayer"
                    )

                for role_config in SERVICE_CONFIG[
                    "Prayer"
                ]:

                    for _ in range(
                        role_config["count"]
                    ):

                        self.assign_role(
                            date,
                            campus,
                            role_config,
                            daily_used_people,
                            "Prayer"
                        )

            # =====================================
            # SUNDAY SERVICES
            # =====================================

            else:

                for campus in CAMPUSES:

                    # -----------------------------
                    # PASS 1 — DIRECTORS
                    # -----------------------------

                    current_step += 1

                    if progress_callback:

                        progress_callback(
                            current_step / total_steps,
                            f"{date} | {campus} | Directors"
                        )

                    for role_config in SERVICE_CONFIG[
                        "Sunday"
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
                                daily_used_people,
                                "Sunday"
                            )

                    # -----------------------------
                    # PASS 2 — MAIN
                    # -----------------------------

                    current_step += 1

                    if progress_callback:

                        progress_callback(
                            current_step / total_steps,
                            f"{date} | {campus} | Main Roles"
                        )

                    for role_config in SERVICE_CONFIG[
                        "Sunday"
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
                                daily_used_people,
                                "Sunday"
                            )

                    # -----------------------------
                    # PASS 3 — ASSISTANTS
                    # -----------------------------

                    current_step += 1

                    if progress_callback:

                        progress_callback(
                            current_step / total_steps,
                            f"{date} | {campus} | Assistants"
                        )

                    for role_config in SERVICE_CONFIG[
                        "Sunday"
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
                                daily_used_people,
                                "Sunday"
                            )

        # =========================================
        # REPAIR PASS
        # =========================================

        repair_schedule(
            self.schedule,
            self.skills_df,
            self.availability_df,
            self.assignments
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

            "date_order":
                self.date_columns
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
