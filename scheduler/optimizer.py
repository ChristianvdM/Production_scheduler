CAMPUSES = [
    "Tygerberg",
    "Stellies",
    "Paarl"
]

SERVICE_CONFIG = {
    "Sunday": [
        {
            "role": "Director",
            "type": "director",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Sound",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Lights",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Resi",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Sound Assistant",
            "type": "assistant",
            "min_skill": 0.1,
            "max_skill": 1.99,
            "count": 1
        }
    ],

    "Prayer": [
        {
            "role": "Sound",
            "type": "main",
            "min_skill": 2,
            "count": 1
        },

        {
            "role": "Sound Assistant",
            "type": "assistant",
            "min_skill": 0.1,
            "max_skill": 1.99,
            "count": 2
        },

        {
            "role": "Runner",
            "type": "runner",
            "count": 1
        }
    ]
}
