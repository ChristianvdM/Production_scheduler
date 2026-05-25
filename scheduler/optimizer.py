import pandas as pd
from collections import defaultdict
from datetime import datetime

from scheduler.loaders import normalize_name

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]

ROLES_SUNDAY = [
    "Sound",
    "Lights",
    "Resi"
]

# ---------------------------------------------------
# MAIN SCHEDULER
# ---------------------------------------------------

def generate_schedule(
    skills_df,
    availability_df,
    progress_callback=None
):

    def update_progress(
        progress,
        message
    ):

        if progress_callback:

            progress_callback(
                progress,
                message
            )

    update_progress(
        0.05,
        "Preparing scheduler..."
    )

    # ---------------------------------------------------
    # DATE COLUMNS
    # ---------------------------------------------------

    date_columns = [

        col for col in availability_df.columns

        if col not in [
            "Name",
            "Name_Normalized"
        ]
    ]

    sunday_dates = []

    for d in date_columns:

        try:

            parsed = datetime.strptime(
                str(d),
                "%Y-%m-%d"
            )

            if parsed.weekday() == 6:

                sunday_dates.append(d)

        except:
            pass

    # ---------------------------------------------------
    # STORAGE
    # ---------------------------------------------------

    schedule = {}

    for campus in CAMPUSES:

        schedule[f"{campus}_Sunday"] = {

            d: {}

            for d in sunday_dates
        }

    assignments = []

    assignment_counts = defaultdict(int)

    # ---------------------------------------------------
    # HELPERS
    # ---------------------------------------------------

    def get_available_people(date):

        return availability_df[

            availability_df[date]
            .astype(str)
            .str.strip()
            .str.lower()
            == "yes"

        ]["Name"].tolist()

    def get_skill(
        person,
        skill_col
    ):

        person_norm = normalize_name(
            person
        )

        matches = skills_df.loc[

            skills_df["Name_Normalized"]
            == person_norm

        ]

        if matches.empty:
            return 0

        value = matches.iloc[0].get(
            skill_col,
            0
        )

        try:
            return float(value)

        except:
            return 0

    def get_best_person(
        people,
        skill_col,
        used_people
    ):

        candidates = []

        for person in people:

            if person in used_people:
                continue

            skill = get_skill(
                person,
                skill_col
            )

            candidates.append(
                (
                    person,
                    skill,
                    assignment_counts[person]
                )
            )

        if not candidates:
            return None

        candidates = sorted(

            candidates,

            key=lambda x: (
                -x[1],
                x[2]
            )
        )

        return candidates[0][0]

    # ---------------------------------------------------
    # ASSIGNMENTS
    # ---------------------------------------------------

    update_progress(
        0.30,
        "Generating assignments..."
    )

    for date in sunday_dates:

        available_people = (
            get_available_people(date)
        )

        for campus in CAMPUSES:

            used_people = set()

            for role in ROLES_SUNDAY:

                skill_col = (
                    f"{role}_{campus}"
                )

                person = get_best_person(
                    available_people,
                    skill_col,
                    used_people
                )

                if person:

                    schedule[
                        f"{campus}_Sunday"
                    ][date][role] = person

                    used_people.add(person)

                    assignment_counts[
                        person
                    ] += 1

                    assignments.append(
                        {
                            "Date": date,
                            "Campus": campus,
                            "Role": role,
                            "Name": person
                        }
                    )

    # ---------------------------------------------------
    # DATAFRAMES
    # ---------------------------------------------------

    update_progress(
        0.80,
        "Building outputs..."
    )

    assignments_df = pd.DataFrame(
        assignments
    )

    if assignments_df.empty:

        summary_df = pd.DataFrame()

    else:

        summary_df = assignments_df.groupby(
            ["Name", "Campus"]
        ).size().reset_index(
            name="Assignments"
        )

    update_progress(
        1.0,
        "Complete"
    )

    return {

        "schedule": schedule,

        "assignments": assignments_df,

        "summary": summary_df
    }
