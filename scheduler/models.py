from dataclasses import dataclass


# =========================================================
# ASSIGNMENT MODEL
# =========================================================

@dataclass
class Assignment:
    volunteer: str
    campus: str
    role: str
    service_type: str
    date: str


# =========================================================
# HISTORICAL ASSIGNMENT MODEL
# =========================================================

@dataclass
class HistoricalAssignment:
    volunteer: str
    campus: str
    role: str
    service_type: str
    date: str


# =========================================================
# SERVICE CONFIGURATION
# =========================================================

SERVICE_CONFIG = {

    # =====================================================
    # SUNDAY SERVICES
    # =====================================================

    "Sunday": {

        "campuses": [
            "Tygerberg",
            "Stellies",
            "Paarl"
        ],

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

    # =====================================================
    # PRAYER NIGHTS
    # =====================================================

    "Prayer": {

        "campuses": [
            "Tygerberg"
        ],

        "roles": [

            "Director",

            "Sound",

            "Lights",

            "Resi",

            "Assistant",

            # NEW
            "Production Setup 1",
            "Production Setup 2"
        ]
    }
}
