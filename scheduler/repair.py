from copy import deepcopy

from scheduler.evaluator import evaluate_schedule


def optimize_schedule(
    state,
    metrics,
    iterations=200
):

    best_state = deepcopy(state)

    best_score = evaluate_schedule(
        best_state,
        metrics
    )

    for _ in range(iterations):

        candidate = deepcopy(best_state)

        improved = attempt_swap(candidate)

        if not improved:
            continue

        candidate_score = evaluate_schedule(
            candidate,
            metrics
        )

        if candidate_score > best_score:

            best_state = candidate

            best_score = candidate_score

    return best_state


def attempt_swap(state):

    volunteers = list(state.by_volunteer.keys())

    if len(volunteers) < 2:
        return False

    v1 = volunteers[0]
    v2 = volunteers[-1]

    if not state.by_volunteer[v1]:
        return False

    if not state.by_volunteer[v2]:
        return False

    a1 = state.by_volunteer[v1][0]
    a2 = state.by_volunteer[v2][0]

    a1.volunteer, a2.volunteer = (
        a2.volunteer,
        a1.volunteer
    )

    return True
