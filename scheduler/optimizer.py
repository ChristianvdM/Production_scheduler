from collections import defaultdict

from scheduler.models import Assignment
from scheduler.scoring import calculate_candidate_score


def get_skill(skills_df, volunteer, column):

    row = skills_df.loc[skills_df["Name"] == volunteer]

    if row.empty:
        return 0

    return int(row[column].values[0])


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

        skill_level = get_skill(skills_df, volunteer, skill_column)

        if skill_level <= 0:
            continue

        score = calculate_candidate_score(
            volunteer=volunteer,
            role=role,
            campus=campus,
            skill_level=skill_level,
            metrics=metrics
        )

        ranked.append((volunteer, score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return [r[0] for r in ranked]


def assign_role(
    assignments,
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
        candidates,
        role,
        campus,
        skill_column,
        skills_df,
        metrics
    )

    selected = next(
        (p for p in ranked if p not in used_people),
        None
    )

    if selected:

        assignments.append(
            Assignment(
                volunteer=selected,
                campus=campus,
                role=role,
                service_type=service_type,
                date=date
            )
        )

        used_people.add(selected)

        metrics["served_counts"][selected] += 1

    return selected
