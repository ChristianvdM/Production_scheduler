import streamlit as st
from datetime import datetime

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
    "Upload Actual Served Schedule (Optional)",
    type=["csv", "xlsx", "ods"]
)


# =========================================================
# MAIN EXECUTION
# =========================================================

if skills_file and availability_file:

    try:

        # =================================================
        # LOAD DATA
        # =================================================

        with st.spinner("Loading files..."):

            skills_df = load_skills(skills_file)

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

        with st.spinner(
            "Building historical fairness metrics..."
        ):

            metrics = build_historical_metrics(history)

        # =================================================
        # INITIALIZE SCHEDULE STATE
        # =================================================

        state = ScheduleState()

        # =================================================
        # FIND DATE COLUMNS
        # =================================================

        availability_dates = [
            c for c in availability_df.columns
            if c != "Name"
        ]

        # =================================================
        # GENERATE INITIAL SCHEDULE
        # =================================================

        with st.spinner(
            "Generating initial schedule..."
        ):

            for date in availability_dates:

                try:

                    weekday = datetime.strptime(
                        date,
                        "%Y-%m-%d"
                    ).weekday()

                except Exception:
                    continue

                # =========================================
                # DETERMINE SERVICE TYPE
                # =========================================

                service_type = None

                # Sunday
                if weekday == 6:
                    service_type = "Sunday"

                # Saturday / Prayer
                elif weekday == 5:
                    service_type = "Prayer"

                if service_type is None:
                    continue

                config = SERVICE_CONFIG[
                    service_type
                ]

                # =========================================
                # AVAILABLE PEOPLE
                # =========================================

                available_people = availability_df[
                    availability_df[date] == "Yes"
                ]["Name"].tolist()

                # =========================================
                # PROCESS CAMPUSES
                # =========================================

                for campus in config["campuses"]:

                    used_people = set()

                    # =====================================
                    # ROLE ORDERING
                    # Critical roles first
                    # =====================================

                    role_priority = sorted(
                        config["roles"],
                        key=lambda r: (
                            "Director" not in r,
                            "Main" not in r
                        )
                    )

                    for role in role_priority:

                        # ================================
                        # DETERMINE SKILL COLUMN
                        # ================================

                        if role == "Director":

                            skill_column = "Director"

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

                        else:

                            # Assistant fallback
                            skill_column = (
                                f"Sound_{campus}"
                            )

                        # ================================
                        # ASSIGN ROLE
                        # ================================

                        selected = assign_role(
                            assignments=state.assignments,
                            used_people=used_people,
                            candidates=available_people,
                            role=role,
                            campus=campus,
                            service_type=service_type,
                            date=date,
                            skill_column=skill_column,
                            skills_df=skills_df,
                            metrics=metrics
                        )

                        # ================================
                        # UPDATE STATE
                        # ================================

                        if selected:

                            assignment = next(
                                (
                                    a for a in
                                    state.assignments
                                    if (
                                        a.volunteer == selected
                                        and a.date == date
                                        and a.role == role
                                        and a.campus == campus
                                    )
                                ),
                                None
                            )

                            if assignment:
                                state.add(assignment)

        st.success(
            "Initial schedule generation complete"
        )

        # =================================================
        # OPTIMIZATION PASSES
        # =================================================

        with st.spinner(
            "Optimizing schedule..."
        ):

            state = optimize_schedule(
                state=state,
                metrics=metrics,
                iterations=500
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
                "Date": a.date,
                "Campus": a.campus,
                "Service": a.service_type,
                "Role": a.role,
                "Volunteer": a.volunteer
            })

        if preview_rows:

            import pandas as pd

            preview_df = pd.DataFrame(
                preview_rows
            )

            preview_df = preview_df.sort_values(
                by=["Date", "Campus", "Role"]
            )

            st.markdown(
                "## 📋 Schedule Preview"
            )

            st.dataframe(
                preview_df,
                use_container_width=True
            )

        # =================================================
        # EXPORT
        # =================================================

        with st.spinner(
            "Building Excel export..."
        ):

            excel_data = export_schedule(
                state.assignments
            )

        st.success(
            "Schedule successfully generated"
        )

        # =================================================
        # DOWNLOAD BUTTON
        # =================================================

        st.download_button(
            label="📥 Download Schedule",
            data=excel_data,
            file_name="production_schedule.xlsx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            )
        )

        # =================================================
        # METRICS DASHBOARD
        # =================================================

        st.markdown("## 📊 Historical Metrics")

        served_counts = metrics["served_counts"]

        cancellation_counts = metrics["cancellations"]

        dashboard_rows = []

        volunteers = sorted(
            set(
                list(served_counts.keys())
                +
                list(cancellation_counts.keys())
            )
        )

        for volunteer in volunteers:

            scheduled = metrics[
                "scheduled_counts"
            ][volunteer]

            served = served_counts[
                volunteer
            ]

            cancelled = cancellation_counts[
                volunteer
            ]

            reliability = round(
                (
                    served /
                    scheduled
                ) * 100,
                1
            ) if scheduled > 0 else 100

            dashboard_rows.append({
                "Volunteer": volunteer,
                "Scheduled": scheduled,
                "Served": served,
                "Cancelled": cancelled,
                "Reliability %": reliability
            })

        if dashboard_rows:

            metrics_df = pd.DataFrame(
                dashboard_rows
            )

            metrics_df = metrics_df.sort_values(
                by=[
                    "Reliability %",
                    "Served"
                ],
                ascending=[False, False]
            )

            st.dataframe(
                metrics_df,
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"Error generating schedule: {e}"
        )

        st.exception(e)
