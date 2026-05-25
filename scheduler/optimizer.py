import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime

from scheduler.loaders import normalize_name

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

CAMPUS = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]

ROLES_SUNDAY = [
    "Sound",
    "Lights",
    "Resi"
]

ROLES_SATURDAY = [
    "Sound",
    "Lights",
    "Resi",
    "Assistant"
]

MAX_SUNDAYS = 3
MAX_SATURDAYS = 3

# ---------------------------------------------------
# MAIN SCHEDULER
# ---------------------------------------------------

def generate_schedule(
    skills_df,
    availability_df,
    progress_callback=None
):

    # ---------------------------------------------------
    # PROGRESS HELPER
    # ---------------------------------------------------

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
        "Preparing scheduling engine..."
    )

    # ---------------------------------------------------
    # DATE DETECTION
    # ---------------------------------------------------

    date_columns = [

        col for col in availability_df.columns

        if col not in [
            "Name",
            "Name_Normalized"
        ]
    ]

    saturday_dates = []
    sunday_dates = []

    for d in date_columns:

        try:

            parsed = datetime.strptime(
                str(d),
                "%Y-%m-%d"
            )

            if parsed.weekday() == 5:
                saturday_dates.append(d)

            elif parsed.weekday() == 6:
                sunday_dates.append(d)

        except:
            continue

    # ---------------------------------------------------
    # STORAGE
    # ---------------------------------------------------

    schedule = {}

    for campus in CAMPUS:

        schedule[f"{campus}_Sunday"] = {
            d: {} for d in sunday_dates
        }

    schedule["Tygerberg_Saturday"] = {
        d: {} for d in saturday_dates
    }

    assignments_count = defaultdict(int)

    assignment_log = defaultdict(
        lambda: {
            "Sunday": 0,
            "Saturday": 0
        }
    )

    detailed_assignments = []

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

    def get_person_row(person):

        person_norm = normalize_name(
            person
        )

        matches = skills_df.loc[

            skills_df["Name_Normalized"]
            == person_norm

        ]

        if matches.empty:
            return None

        return matches.iloc[0]

    def get_skill(person, col):

        row = get_person_row(person)

        if row is None:
            return 0

        value = row.get(col, 0)

        try:
            return float(value)

        except:
            return 0

    def get_eligible(
        people,
        col,
        minimum_skill
    ):

        eligible = []

        for person in people:

            skill = get_skill(
                person,
                col
            )

            if skill >= minimum_skill:
                eligible.append(person)

        return eligible

    def get_least_assigned(people):

        return sorted(
            people,
            key=lambda p: (
                assignments_count[p]
            )
        )

    def assign_person(
        person,
        campus,
        role,
        service_day,
        schedule_key,
        date,
        role_key
    ):

        schedule[
            schedule_key
        ][date][role_key] = person

        assignments_count[
            person
        ] += 1

        assignment_log[
            person
        ][service_day] += 1

        detailed_assignments.append(
            (
                person,
                campus,
                role,
                service_day,
                date
            )
        )

    # ---------------------------------------------------
    # ASSIGN DIRECTORS FIRST
    # ---------------------------------------------------

    update_progress(
        0.15,
        "Assigning directors..."
    )

    all_dates = (
        saturday_dates
        + sunday_dates
    )

    for date in all_dates:

        all_available = get_available_people(
            date
        )

        # ---------------------------------------------------
        # SATURDAY
        # ---------------------------------------------------

        if date in saturday_dates:

            under_limit = [

                p for p in all_available

                if assignment_log[p]["Saturday"]
                < MAX_SATURDAYS
            ]

            eligible = get_eligible(
                under_limit,
                "Director",
                2
            )

            if not eligible:

                eligible = get_eligible(
                    all_available,
                    "Director",
                    2
                )

            if not eligible:

                eligible = all_available

            director = next(

                iter(
                    get_least_assigned(
                        eligible
                    )
                ),

                None
            )

            if director:

                assign_person(
                    director,
                    "Tygerberg",
                    "Director",
                    "Saturday",
                    "Tygerberg_Saturday",
                    date,
                    "Director"
                )

        # ---------------------------------------------------
        # SUNDAY
        # ---------------------------------------------------

        if date in sunday_dates:

            for campus in CAMPUS:

                under_limit = [

                    p for p in all_available

                    if assignment_log[p]["Sunday"]
                    < MAX_SUNDAYS
                ]

                eligible = get_eligible(
                    under_limit,
                    "Director",
                    2
                )

                if not eligible:

                    eligible = get_eligible(
                        all_available,
                        "Director",
                        2
                    )

                if not eligible:

                    eligible = all_available

                director = next(

                    iter(
                        get_least_assigned(
                            eligible
                        )
                    ),

                    None
                )

                if director:

                    assign_person(
                        director,
                        campus,
                        "Director",
                        "Sunday",
                        f"{campus}_Sunday",
                        date,
                        "Director"
                    )

    # ---------------------------------------------------
    # ASSIGN SUNDAY ROLES
    # ---------------------------------------------------

    update_progress(
        0.40,
        "Assigning Sunday teams..."
    )

    for date in sunday_dates:

        all_available = get_available_people(
            date
        )

        for campus in CAMPUS:

            used = set(

                schedule[
                    f"{campus}_Sunday"
                ][date].values()

            )

            for role in ROLES_SUNDAY:

                col = f"{role}_{campus}"

                # ---------------------------------------------------
                # MAIN
                # ---------------------------------------------------

                under_limit = [

                    p for p in all_available

                    if assignment_log[p]["Sunday"]
                    < MAX_SUNDAYS
                ]

                eligible_main = get_eligible(
                    under_limit,
                    col,
                    2
                )

                main_candidates = [

                    p for p in
                    get_least_assigned(
                        eligible_main
                    )

                    if p not in used
                ]

                if not main_candidates:

                    eligible_main = get_eligible(
                        all_available,
                        col,
                        2
                    )

                    main_candidates = [

                        p for p in
                        get_least_assigned(
                            eligible_main
                        )

                        if p not in used
                    ]

                main = next(
                    iter(main_candidates),
                    None
                )

                if main:

                    assign_person(
                        main,
                        campus,
                        f"{role} Main",
                        "Sunday",
                        f"{campus}_Sunday",
                        date,
                        f"{role} Main"
                    )

                    used.add(main)

                # ---------------------------------------------------
                # ASSISTANT
                # ---------------------------------------------------

                eligible_assist = get_eligible(
                    all_available,
                    col,
                    1
                )

                assist_candidates = [

                    p for p in
                    get_least_assigned(
                        eligible_assist
                    )

                    if (
                        p not in used
                        and p != main
                    )
                ]

                assist = next(
                    iter(assist_candidates),
                    None
                )

                if assist:

                    assign_person(
                        assist,
                        campus,
                        f"{role} Assistant",
                        "Sunday",
                        f"{campus}_Sunday",
                        date,
                        f"{role} Assistant"
                    )

                    used.add(assist)

    # ---------------------------------------------------
    # ASSIGN SATURDAY ROLES
    # ---------------------------------------------------

    update_progress(
        0.70,
        "Assigning Saturday teams..."
    )

    for date in saturday_dates:

        all_available = get_available_people(
            date
        )

        used = set(

            schedule[
                "Tygerberg_Saturday"
            ][date].values()

        )

        for role in [

            "Sound",
            "Lights",
            "Resi"

        ]:

            col = f"{role}_Tygerberg"

            under_limit = [

                p for p in all_available

                if assignment_log[p]["Saturday"]
                < MAX_SATURDAYS
            ]

            eligible = get_eligible(
                under_limit,
                col,
                2
            )

            main_candidates = [

                p for p in
                get_least_assigned(
                    eligible
                )

                if p not in used
            ]

            if not main_candidates:

                eligible = get_eligible(
                    all_available,
                    col,
                    2
                )

                main_candidates = [

                    p for p in
                    get_least_assigned(
                        eligible
                    )

                    if p not in used
                ]

            main = next(
                iter(main_candidates),
                None
            )

            if main:

                assign_person(
                    main,
                    "Tygerberg",
                    role,
                    "Saturday",
                    "Tygerberg_Saturday",
                    date,
                    role
                )

                used.add(main)

        # ---------------------------------------------------
        # SATURDAY ASSISTANT
        # ---------------------------------------------------

        def total_skill(person):

            row = get_person_row(person)

            if row is None:
                return 0

            cols = [

                "Sound_Tygerberg",
                "Lights_Tygerberg",
                "Resi_Tygerberg",
                "Director"
            ]

            total = 0

            for c in cols:

                try:
                    total += float(
                        row.get(c, 0)
                    )
                except:
                    pass

            return total

        eligible_assist = [

            p for p in all_available

            if (
                p not in used
                and any(

                    get_skill(p, c) >= 1

                    for c in [
                        "Sound_Tygerberg",
                        "Lights_Tygerberg",
                        "Resi_Tygerberg"
                    ]
                )
            )
        ]

        eligible_assist = sorted(

            eligible_assist,

            key=lambda p: (
                assignments_count[p],
                total_skill(p)
            )
        )

        assistant = next(
            iter(eligible_assist),
            None
        )

        if assistant:

            assign_person(
                assistant,
                "Tygerberg",
                "Assistant",
                "Saturday",
                "Tygerberg_Saturday",
                date,
                "Assistant"
            )

    # ---------------------------------------------------
    # BUILD DATAFRAMES
    # ---------------------------------------------------

    update_progress(
        0.90,
        "Building schedule outputs..."
    )

    assignments_df = pd.DataFrame(

        detailed_assignments,

        columns=[
            "Name",
            "Campus",
            "Role",
            "Day",
            "Date"
        ]
    )

    if assignments_df.empty:

        summary_df = pd.DataFrame()

    else:

        summary_df = assignments_df.groupby(
            ["Name", "Campus"]
        ).size().reset_index(
            name="Assignments"
        )

    # ---------------------------------------------------
    # RESULTS
    # ---------------------------------------------------

    update_progress(
        1.0,
        "Schedule complete"
    )

    return {

        "schedule": schedule,

        "assignments": assignments_df,

        "summary": summary_df,

        "assignment_counts": dict(
            assignments_count
        )
    }
