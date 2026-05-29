def evaluate_schedule(state, metrics):

    score = 0

    score += evaluate_coverage(state)

    score += evaluate_fairness(state)

    score += evaluate_proficiency(state)

    score += evaluate_campus_balance(state)

    return score


def evaluate_coverage(state):

    filled_roles = len(state.assignments)

    return filled_roles * 100


def evaluate_fairness(state):

    counts = [
        len(v)
        for v in state.by_volunteer.values()
    ]

    if not counts:
        return 0

    spread = max(counts) - min(counts)

    return -spread * 50


def evaluate_proficiency(state):

    # placeholder

    return 0


def evaluate_campus_balance(state):

    # placeholder

    return 0
