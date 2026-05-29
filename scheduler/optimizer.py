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
# ASSISTANT CHECK
# =========================================================

def is_assistant_role(role):

    return (
        "assistant"
        in str(role).lower()
    )


# =========================================================
# RUNNER CHECK
# =========================================================

def is_setup_role(role):

    role = str(role).lower()

    return (
        "production setup" in role
        or "runner" in role
    )


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

        skill_level = get_skill(
            skills_df,
            volunteer,
            skill_column
        )

        # =============================================
        # RUNNERS PREFER LOWER SKILLS
        # =============================================

        if is_runner_role(role):

            adjusted_skill = (
                6 - skill_level
            )

        else:

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

            adjusted_skill = skill_level

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

    ranked.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [
        r[0]
        for r in ranked
    ]


# =========================================================
# CHECK SAME-DAY CONFLICTS
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

        metrics["served_counts"][
            selected
        ] += 1

    return selected
