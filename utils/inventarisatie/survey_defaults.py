SURVEY_DEFAULTS = {
    "mussen/spreeuwen": {
        "type": "toggle_group",
        "default": False,
        "fields": {
            "aantal_rondes": 0,
            "aantal_personen": 0,
            "uren_per_survey": 0
        }
    },

    "gierzwaluwen": {
        "type": "toggle_group",
        "default": False,
        "fields": {
            "aantal_rondes": 0,
            "aantal_personen": 0,
            "uren_per_survey": 0
        }
    },

    "vleermuizen": {
        "type": "multi_phase",
        "phases": {
            "ochtend": {
                "aantal_rondes": 0,
                "aantal_personen": 0,
                "uren_per_survey": 0
            },
            "avond": {
                "aantal_rondes": 0,
                "aantal_personen": 0,
                "uren_per_survey": 0
            },
            "paarperiode": {
                "aantal_rondes": 0,
                "aantal_personen": 0,
                "uren_per_survey": 0
            }
        }
    }
}


