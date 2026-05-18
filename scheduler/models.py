from dataclasses import dataclass
from typing import Optional


# -------------------------------------------------
# SINGLE ASSIGNMENT
# -------------------------------------------------

@dataclass
class Assignment:

    date: str

    campus: str

    service: str

    role: str

    person: str

    skill: float

    score: float


# -------------------------------------------------
# ROLE CONFIGURATION
# -------------------------------------------------

@dataclass
class RoleConfig:

    role: str

    role_type: str

    min_skill: float = 0

    max_skill: float = 999

    count: int = 1


# -------------------------------------------------
# VOLUNTEER METRICS
# -------------------------------------------------

@dataclass
class VolunteerStats:

    name: str

    total_assignments: int = 0

    tygerberg_count: int = 0

    stellies_count: int = 0

    paarl_count: int = 0

    assistant_count: int = 0

    sunday_count: int = 0

    prayer_count: int = 0

    fairness_delta: float = 0


# -------------------------------------------------
# SCHEDULE METRICS
# -------------------------------------------------

@dataclass
class ScheduleMetrics:

    coverage_rate: float

    unfilled_roles: int

    fairness_std_dev: float

    avg_skill_score: float

    total_assignments: int

    unique_volunteers: int


# -------------------------------------------------
# UNFILLED ROLE TRACKER
# -------------------------------------------------

@dataclass
class UnfilledRole:

    date: str

    campus: str

    service: str

    role: str

    reason: Optional[str] = None


# -------------------------------------------------
# CANDIDATE SCORE
# -------------------------------------------------

@dataclass
class CandidateScore:

    person: str

    score: float

    skill: float

    fairness_score: float = 0

    proficiency_score: float = 0

    fatigue_penalty: float = 0

    elite_penalty: float = 0

    campus_balance_score: float = 0


# -------------------------------------------------
# EXPORT CONFIG
# -------------------------------------------------

@dataclass
class ExportConfig:

    include_summary: bool = True

    include_assignments: bool = True

    include_fairness_sheet: bool = True

    include_service_sheets: bool = True

    include_campus_sheets: bool = True


# -------------------------------------------------
# SERVICE CONFIG
# -------------------------------------------------

@dataclass
class ServiceDefinition:

    service_name: str

    roles: list

    campuses: list


# -------------------------------------------------
# REPAIR ACTION
# -------------------------------------------------

@dataclass
class RepairAction:

    date: str

    campus: str

    role: str

    old_person: Optional[str]

    new_person: Optional[str]

    reason: str
