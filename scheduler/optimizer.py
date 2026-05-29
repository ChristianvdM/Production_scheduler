from scheduler.models import (
    Assignment
)

from scheduler.scoring import (
    calculate_candidate_score
)


# =========================================================
# GET SKILL LEVEL
# =========================================================

def get_skill(
    skills_df,
    volunteer,
    column
):

    row = skills_df[
        skills_df["Name"] == volunteer
    ]

    if row.empty:
        return 0

    try:

        value = row[column].values[0]

        return int(value)

    except:
        return 0


# =========================================================
# ROLE HELPERS
# =========================================================

def is_assistant_role(role):

    return (
        "assistant"
        in str(role).lower()
    )


def is_runner_role(role):

    return (
        "runner"
        in str(role).lower()
    )


def is_setup_role(role):

    return (
        "production setup"
        in str(role).lower()
    )


# =========================================================
# SAME DAY CHECK
# =========================================================

def already_scheduled_same_day(
    state,
    volunteer,
    date
):

    for assignment in state.assignments:

        if (
            assignment.volunteer == volunteer
            and assignment.date == date
        ):
            return True

    return False


# =========================================================
# RANK CANDIDATES
# =========================================================

def rank_candidates(

    candidates,

    role,

    campus,

    skill_column,

    skills_df,

    metrics
):

    ranked = []

    for volunteer in candidates:

        # =============================================
        # ROLE SKILL
        # =============================================

        skill_level = get_skill(
            skills_df,
            volunteer,
            skill_column
        )

        # =============================================
        # DIRECTOR SKILL
        # =============================================

        director_skill = get_skill(
            skills_df,
            volunteer,
            "Director"
        )

        # =============================================
        # RUNNERS / SETUP
        # =============================================

        if (
            is_runner_role(role)
            or is_setup_role(role)
        ):

            # =========================================
            # DIRECTOR LEVEL 3 CANNOT DO:
            # - runners
            # - setup
            # =========================================

            if director_skill >= 3:
                continue

            adjusted_skill = (
                6 - skill_level
            )

        else:

            # =========================================
            # REQUIRE BASIC SKILL
            # =========================================

            if skill_level <= 0:
                continue

            # =========================================
            # HIGH SKILL CANNOT ASSIST
            # =========================================

            if (
                is_assistant_role(role)
                and skill_level > 2
            ):
                continue

            # =========================================
            # DIRECTOR LEVEL 3
            # CANNOT ASSIST
            # =========================================

            if (
                is_assistant_role(role)
                and director_skill >= 3
            ):
                continue

            adjusted_skill = skill_level

        # =============================================
        # CALCULATE SCORE
        # =============================================

        score = calculate_candidate_score(

            volunteer=volunteer,

            role=role,

            campus=campus,

            skill_level=adjusted_skill,

            metrics=metrics
        )

        ranked.append(
            (
                volunteer,
                score
            )
        )

    # ================================================
    # SORT BEST FIRST
    # ================================================

    ranked.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [
        r[0]
        for r in ranked
    ]


# =========================================================
# ASSIGN ROLE
# =========================================================

def assign_role(

    state,

    used_people,

    candidates,

    role,

    campus,

    service_type,

    date,

    skill_column,

    skills_df,

    metrics
):

    ranked = rank_candidates(

        candidates=candidates,

        role=role,

        campus=campus,

        skill_column=skill_column,

        skills_df=skills_df,

        metrics=metrics
    )

    # =====================================================
    # FIND FIRST VALID PERSON
    # =====================================================

    selected = next(

        (
            p for p in ranked

            if (
                p not in used_people

                and not already_scheduled_same_day(
                    state,
                    p,
                    date
                )
            )
        ),

        None
    )

    # =====================================================
    # CREATE ASSIGNMENT
    # =====================================================

    if selected:

        assignment = Assignment(

            volunteer=selected,

            campus=campus,

            role=role,

            service_type=service_type,

            date=date
        )

        state.add(
            assignment
        )

        used_people.add(
            selected
        )

        # =================================================
        # UPDATE METRICS
        # =================================================

        metrics["served_counts"][
            selected
        ] += 1

        metrics["campus_counts"][
            (
                selected,
                campus
            )
        ] += 1

    return selected
