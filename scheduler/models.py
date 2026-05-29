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
    # TYGERBERG
    # =====================================================

    "Sunday_Tygerberg": {

        "campuses": [
            "Tygerberg"
        ],

        "roles": [

            "Director",

            "Sound",
            "Sound Assistant",

            "Lights",

            "Resi",

            "Runner"
        ]
    },

    # =====================================================
    # STELLIES
    # =====================================================

    "Sunday_Stellies": {

        "campuses": [
            "Stellies"
        ],

        "roles": [

            "Director",

            "Sound",
            "Sound Assistant",

            "Lights",
            "Lights Assistant",

            "Resi",

            "Runner"
        ]
    },

    # =====================================================
    # PAARL
    # =====================================================

    "Sunday_Paarl": {

        "campuses": [
            "Paarl"
        ],

        "roles": [

            "Director",

            "Sound",
            "Sound Assistant",

            "Lights",

            "Resi",

            "Runner"
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
            "Sound Assistant",

            "Lights",

            "Resi",

            "Runner 1",
            "Runner 2"
        ]
    }
}
