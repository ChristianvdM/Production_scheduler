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
# ASSISTANT ROLE CHECK
# =========================================================

def is_assistant_role(role):

    role = str(role).lower()

    return (
        "assistant" in role
    )


# =========================================================
# PRODUCTION SETUP ROLE CHECK
# =========================================================

def is_production_setup_role(role):

    return (
        "production setup"
        in str(role).lower()
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
        # REQUIRE BASIC SKILL
        # =============================================

        if skill_level <= 0:
            continue

        # =============================================
        # NEW RULE:
        # HIGH SKILL CANNOT DO ASSISTANT
        # =============================================

        if (
            is_assistant_role(role)
            and skill_level > 2
        ):
            continue

        # =============================================
        # NEW RULE:
        # PRODUCTION SETUP PREFERS LOW SKILL
        # =============================================

        if is_production_setup_role(role):

            # Strong preference for lower skill
            adjusted_skill = (
                6 - skill_level
            )

        else:

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

            if p not in used_people
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
