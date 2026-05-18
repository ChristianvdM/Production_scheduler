from dataclasses import dataclass


@dataclass
class Assignment:
    date: str
    campus: str
    role: str
    person: str
    score: float
    skill: float
