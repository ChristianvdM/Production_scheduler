import streamlit as st
import pandas as pd

from scheduler.loaders import (
    load_skills,
    load_availability,
    load_actual_schedule
)

from scheduler.metrics import (
    build_historical_metrics
)

from scheduler.optimizer import (
    assign_role
)

from scheduler.repair import (
    optimize_schedule
)

from scheduler.exports import (
    export_schedule
)

from scheduler.models import (
    SERVICE_CONFIG
)

from scheduler.state import (
    ScheduleState
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CPT Production Scheduler",
    layout="wide"
)

st.title("📅 CPT Production Scheduler")

st.markdown("""
This scheduler optimizes:
- Fair volunteer rotation
- Role coverage
- Skill proficiency
- Campus distribution

Rules:
- Volunteers cannot serve on two campuses on the same day
- High-skilled operators cannot serve as assistants
- Prayer nights include two runners
- Volunteers must exist in BOTH:
  - skills file
  - availability file
""")


# =========================================================
# FILE UPLOADS
# =========================================================

skills_file = st.file_uploader(
    "Upload Skills File",
    type=["csv", "xlsx", "ods"]
)

availability_file = st.file_uploader(
    "Upload Availability File",
    type=["csv", "xlsx", "ods"]
)

actual_schedule_file = st.file_uploader(
    "Upload Historical Actual Schedule (Optional)",
    type=["csv", "xlsx", "ods"]
)


# =========================================================
# MAIN EXECUTION
# =========================================================

if skills_file and availability_file:

    try:

        # =================================================
        # LOAD FILES
        # =================================================

        with st.spinner("Loading files..."):

            skills_df = load_skills(
                skills_file
            )

            availability_df = load_availability(
                availability_file
            )

            history = load_actual_schedule(
                actual_schedule_file
            )

        # =================================================
        # NORMALIZE NAMES
        # =================================================

        skills_df["Name"] = (

            skills_df["Name"]
            .astype(str)
            .str.strip()
        )

        availability_df["Name"] = (

            availability_df["Name"]
            .astype(str)
            .str.strip()
        )

        st.success("Files loaded successfully")

        # =================================================
        # BUILD HISTORICAL METRICS
        # =================================================

        metrics = build_historical_metrics(
            history
        )

        # =================================================
        # INITIALIZE STATE
        # =================================================

        state = ScheduleState()

        # =================================================
        # FIND SERVICE COLUMNS
        # =================================================

        availability_dates = [

            c for c in availability_df.columns

            if str(c).strip() not in [
                "",
                "Name"
            ]
        ]

        # =================================================
        # GENERATE SCHEDULE
        # =================================================

        with st.spinner(
            "Generating schedule..."
        ):

            for date in availability_dates:

                date_str = str(date).strip()

                # =========================================
                # DETERMINE CONFIGS
                # =========================================

                service_configs = []

                if "Prayer" in date_str:

                    service_configs = [
                        (
                            "Prayer",
                            "Tygerberg"
                        )
                    ]

                elif "Services" in date_str:

                    service_configs = [

                        (
                            "Sunday_Tygerberg",
                            "Tygerberg"
                        ),

                        (
                            "Sunday_Stellies",
                            "Stellies"
                        ),

                        (
                            "Sunday_Paarl",
                            "Paarl"
                        )
                    ]

                if not service_configs:
                    continue

                # =========================================
                # AVAILABLE PEOPLE
                # =========================================

                available_values = (

                    availability_df[date]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

                available_people = availability_df[

                    available_values.isin([

                        "yes",
                        "y",
                        "true",
                        "1",
                        "available",
                        "x"
                    ])

                ]["Name"].astype(str).str.strip().tolist()

                # =========================================
                # ONLY USE PEOPLE IN BOTH FILES
                # =========================================

                skills_people = set(

                    skills_df["Name"]
                    .astype(str)
                    .str.strip()
                )

                available_people = [

                    p for p in available_people

                    if p in skills_people
                ]

                # =========================================
                # PROCESS CONFIGS
                # =========================================

                for config_key, campus in service_configs:

                    config = SERVICE_CONFIG[
                        config_key
                    ]

                    used_people = set()

                    # =====================================
                    # PRIORITY ORDER
                    # =====================================

                    role_priority = sorted(

                        config["roles"],

                        key=lambda r: (

                            "Director" not in r,

                            "Sound" not in r,

                            "Lights" not in r,

                            "Resi" not in r
                        )
                    )

                    # =====================================
                    # ASSIGN ROLES
                    # =====================================

                    for role in role_priority:

                        # =================================
                        # MAP ROLE -> SKILL
                        # =================================

                        if role == "Director":

                            skill_column = (
                                "Director"
                            )

                        elif "Sound" in role:

                            skill_column = (
                                f"Sound_{campus}"
                            )

                        elif "Lights" in role:

                            skill_column = (
                                f"Lights_{campus}"
                            )

                        elif "Resi" in role:

                            skill_column = (
                                f"Resi_{campus}"
                            )

                        elif "Runner" in role:

                            # Runner uses
                            # sound skill
                            # as proxy

                            skill_column = (
                                f"Sound_{campus}"
                            )

                        else:

                            skill_column = (
                                f"Sound_{campus}"
                            )

                        # =================================
                        # SKIP INVALID COLUMNS
                        # =================================

                        if (
                            skill_column
                            not in skills_df.columns
                        ):
                            continue

                        # =================================
                        # ASSIGN ROLE
                        # =================================

                        assign_role(

                            state=state,

                            used_people=used_people,

                            candidates=available_people,

                            role=role,

                            campus=campus,

                            service_type=config_key,

                            date=date_str,

                            skill_column=skill_column,

                            skills_df=skills_df,

                            metrics=metrics
                        )

        st.success(
            "Initial schedule generation complete"
        )

        # =================================================
        # OPTIMIZATION
        # =================================================

        with st.spinner(
            "Optimizing schedule..."
        ):

            state = optimize_schedule(

                state=state,

                metrics=metrics,

                iterations=200
            )

        st.success(
            "Optimization complete"
        )

        # =================================================
        # PREVIEW
        # =================================================

        preview_rows = []

        for a in state.assignments:

            preview_rows.append({

                "Date":
                    a.date,

                "Campus":
                    a.campus,

                "Service":
                    a.service_type,

                "Role":
                    a.role,

                "Volunteer":
                    a.volunteer
            })

        st.markdown(
            "## 📋 Schedule Preview"
        )

        if preview_rows:

            preview_df = pd.DataFrame(
                preview_rows
            )

            preview_df = preview_df.sort_values(

                by=[
                    "Date",
                    "Campus",
                    "Role"
                ]
            )

            st.dataframe(
                preview_df,
                use_container_width=True
            )

        else:

            st.warning(
                "No assignments generated."
            )

        # =================================================
        # EXPORT
        # =================================================

        excel_data = export_schedule(
            state.assignments
        )

        st.download_button(

            label="📥 Download Schedule",

            data=excel_data,

            file_name=(
                "production_schedule.xlsx"
            ),

            mime=(
                "application/"
                "vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            )
        )

        # =================================================
        # ASSIGNMENT SUMMARY
        # =================================================

        if preview_rows:

            st.markdown(
                "## 📊 Assignment Summary"
            )

            summary_df = (

                preview_df
                .groupby("Volunteer")
                .size()
                .reset_index(
                    name="Assignments"
                )
                .sort_values(
                    by="Assignments",
                    ascending=False
                )
            )

            st.dataframe(
                summary_df,
                use_container_width=True
            )

        # =================================================
        # HISTORICAL METRICS
        # =================================================

        if history:

            st.markdown(
                "## 📚 Historical Assignment Metrics"
            )

            served_counts = metrics[
                "served_counts"
            ]

            historical_rows = []

            for volunteer, count in (
                served_counts.items()
            ):

                historical_rows.append({

                    "Volunteer":
                        volunteer,

                    "Historical Assignments":
                        count
                })

            historical_df = pd.DataFrame(
                historical_rows
            )

            historical_df = (
                historical_df.sort_values(
                    by="Historical Assignments",
                    ascending=False
                )
            )

            st.dataframe(
                historical_df,
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"Error generating schedule: {e}"
        )

        st.exception(e)
