import pandas as pd


def repair_schedule(
    schedule,
    skills_df,
    availability_df,
    assignments
):

    """
    Placeholder repair engine.

    Future upgrades:
    - assignment swaps
    - fairness balancing
    - campus balancing
    - consecutive week protection
    - unfilled role repair
    - low-skill exposure balancing
    """

    # -------------------------------------------------
    # EMPTY SAFETY
    # -------------------------------------------------

    if not assignments:
        return schedule

    assignments_df = pd.DataFrame(
        assignments
    )

    if assignments_df.empty:
        return schedule

    # -------------------------------------------------
    # REMOVE DUPLICATE ASSIGNMENTS
    # -------------------------------------------------

    assignments_df = assignments_df.drop_duplicates()

    # -------------------------------------------------
    # ENSURE ONE ROLE PER PERSON
    # PER CAMPUS / DATE
    # -------------------------------------------------

    duplicates = assignments_df.duplicated(
        subset=[
            "Date",
            "Campus",
            "Person"
        ],
        keep=False
    )

    duplicate_rows = assignments_df[
        duplicates
    ]

    if not duplicate_rows.empty:

        # Placeholder:
        # Future swap logic can go here

        pass

    # -------------------------------------------------
    # DETECT UNFILLED ROLES
    # -------------------------------------------------

    expected_roles = [
        "Director",
        "Sound",
        "Lights",
        "Resi",
        "Sound Assistant"
    ]

    campuses = [
        "Tygerberg",
        "Stellies",
        "Paarl"
    ]

    dates = assignments_df[
        "Date"
    ].unique()

    unfilled_roles = []

    for date in dates:

        for campus in campuses:

            existing_roles = assignments_df[

                (
                    assignments_df["Date"]
                    == date
                ) &

                (
                    assignments_df["Campus"]
                    == campus
                )

            ]["Role"].tolist()

            for role in expected_roles:

                if role not in existing_roles:

                    unfilled_roles.append({

                        "Date": date,

                        "Campus": campus,

                        "Role": role
                    })

    # -------------------------------------------------
    # FUTURE GAP REPAIR
    # -------------------------------------------------

    # Example future logic:
    #
    # for gap in unfilled_roles:
    #     find_best_swap_candidate()
    #     perform_swap()
    #
    # Current version only reports gaps.

    # -------------------------------------------------
    # FAIRNESS ANALYSIS
    # -------------------------------------------------

    volunteer_counts = assignments_df.groupby(
        "Person"
    ).size()

    fairness_average = volunteer_counts.mean()

    overused = volunteer_counts[
        volunteer_counts >
        fairness_average + 2
    ]

    underused = volunteer_counts[
        volunteer_counts <
        fairness_average - 2
    ]

    # -------------------------------------------------
    # CAMPUS BALANCE ANALYSIS
    # -------------------------------------------------

    campus_distribution = assignments_df.pivot_table(
        index="Person",
        columns="Campus",
        values="Role",
        aggfunc="count",
        fill_value=0
    )

    # -------------------------------------------------
    # LOW PROFICIENCY EXPOSURE ANALYSIS
    # -------------------------------------------------

    assistant_roles = assignments_df[

        assignments_df["Role"]
        .astype(str)
        .str.contains(
            "Assistant",
            case=False,
            na=False
        )
    ]

    assistant_counts = assistant_roles.groupby(
        "Person"
    ).size()

    # -------------------------------------------------
    # STORE REPAIR METADATA
    # -------------------------------------------------

    repair_report = {

        "unfilled_roles": unfilled_roles,

        "overused_volunteers":
            overused.to_dict(),

        "underused_volunteers":
            underused.to_dict(),

        "assistant_distribution":
            assistant_counts.to_dict()
    }

    # -------------------------------------------------
    # ATTACH REPORT
    # -------------------------------------------------

    schedule["repair_report"] = repair_report

    return schedule
