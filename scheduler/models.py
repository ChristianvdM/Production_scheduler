from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Volunteer:
    name: str
    skills: Dict[str, int]


@dataclass
class Assignment:
    volunteer: str
    campus: str
    role: str
    service_type: str
    date: str


@dataclass
class HistoricalAssignment:
    volunteer: str
    campus: str
    role: str
    service_type: str
    date: str
    scheduled: bool = True
    served: bool = True


SERVICE_CONFIG = {
    "Sunday": {
        "campuses": ["Tygerberg", "Stellies", "Paarl"],
        "roles": [
            "Director",
            "Sound Main",
            "Sound Assistant",
            "Lights Main",
            "Lights Assistant",
            "Resi Main",
            "Resi Assistant"
        ]
    },

    "Prayer": {
        "campuses": ["Tygerberg"],
        "roles": [
            "Director",
            "Sound",
            "Lights",
            "Resi",
            "Assistant"
        ]
    }
}
