from collections import defaultdict


class ScheduleState:

    def __init__(self):

        self.assignments = []

        self.by_date = defaultdict(list)

        self.by_volunteer = defaultdict(list)

        self.by_campus = defaultdict(list)

        self.by_role = defaultdict(list)

    def add(self, assignment):

        self.assignments.append(assignment)

        self.by_date[assignment.date].append(assignment)

        self.by_volunteer[assignment.volunteer].append(assignment)

        self.by_campus[assignment.campus].append(assignment)

        self.by_role[assignment.role].append(assignment)

    def remove(self, assignment):

        self.assignments.remove(assignment)

        self.by_date[assignment.date].remove(assignment)

        self.by_volunteer[assignment.volunteer].remove(assignment)

        self.by_campus[assignment.campus].remove(assignment)

        self.by_role[assignment.role].remove(assignment)
