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
- Highly skilled volunteers are protected from assistant roles
- Prayer nights include setup volunteers
- Historical schedules improve future fairness
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
                # DETERMINE SERVICE TYPE
                # =========================================

                service_type = None

                if "Prayer" in date_str:

                    service_type = "Prayer"

                elif "Services" in date_str:

                    service_type = "Sunday"

                if service_type is None:
                    continue

                config = SERVICE_CONFIG[
                    service_type
                ]

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

                ]["Name"].tolist()

                # =========================================
                # PROCESS CAMPUSES
                # =========================================

                for campus in config["campuses"]:

                    used_people = set()

                    # =====================================
                    # PRIORITIZE IMPORTANT ROLES
                    # =====================================

                    role_priority = sorted(

                        config["roles"],

                        key=lambda r: (

                            "Director" not in r,

                            "Main" not in r
                        )
                    )

                    # =====================================
                    # ASSIGN ROLES
                    # =====================================

                    for role in role_priority:

                        # =================================
                        # MAP ROLE TO SKILL COLUMN
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

                        elif (
                            "Production Setup"
                            in role
                        ):

                            # Setup volunteers
                            # use sound skill
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

                            service_type=service_type,

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
        # PREVIEW TABLE
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

            st.info("""
Possible reasons:
- No recognised availability values
- Skill levels are all 0
- Skill columns missing
- Nobody available for required roles
""")

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
