import streamlit as st
from datetime import datetime

from scheduler.loaders import (
    load_skills,
    load_availability,
    load_actual_schedule
)

from scheduler.metrics import build_historical_metrics

from scheduler.optimizer import assign_role

from scheduler.exports import export_schedule

from scheduler.models import SERVICE_CONFIG


st.set_page_config(
    page_title="Production Scheduler",
    layout="wide"
)

st.title("📅 CPT Production Scheduler")


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


if skills_file and availability_file:

    skills_df = load_skills(skills_file)

    availability_df = load_availability(availability_file)

    history = load_actual_schedule(actual_schedule_file)

    metrics = build_historical_metrics(history)

    assignments = []

    availability_dates = [
        c for c in availability_df.columns
        if c != "Name"
    ]

    for date in availability_dates:

        weekday = datetime.strptime(date, "%Y-%m-%d").weekday()

        service_type = None

        if weekday == 6:
            service_type = "Sunday"

        elif weekday == 5:
            service_type = "Prayer"

        if service_type is None:
            continue

        config = SERVICE_CONFIG[service_type]

        available_people = availability_df[
            availability_df[date] == "Yes"
        ]["Name"].tolist()

        for campus in config["campuses"]:

            used_people = set()

            for role in config["roles"]:

                if role == "Director":
                    skill_column = "Director"

                elif "Sound" in role:
                    skill_column = f"Sound_{campus}"

                elif "Lights" in role:
                    skill_column = f"Lights_{campus}"

                elif "Resi" in role:
                    skill_column = f"Resi_{campus}"

                else:
                    skill_column = f"Sound_{campus}"

                assign_role(
                    assignments=assignments,
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

    excel_data = export_schedule(assignments)

    st.success("Schedule Generated")

    st.download_button(
        label="Download Schedule",
        data=excel_data,
        file_name="production_schedule.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
