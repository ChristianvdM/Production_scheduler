import streamlit as st
import pandas as pd
from io import BytesIO
import base64

from scheduler.loaders import load_dataframe
from scheduler.optimizer import generate_schedule
from scheduler.exports import build_excel_output
from scheduler.metrics import build_metrics

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="CPT Production Team Scheduler",
    layout="wide"
)

# ---------------------------------------------------
# DARK THEME
# ---------------------------------------------------

st.markdown(
    """
    <style>

        body {
            background-color: #000000;
            color: white;
        }

        .stApp {
            background-color: #000000;
        }

        .stButton>button,
        .stDownloadButton>button {
            background-color: #444;
            color: white;
        }

        .stMetric {
            background-color: #111;
            padding: 15px;
            border-radius: 10px;
        }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# LOGO
# ---------------------------------------------------

try:

    with open(
        "assets/image.png",
        "rb"
    ) as img_file:

        encoded = base64.b64encode(
            img_file.read()
        ).decode()

        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 20px;'>

                <img
                    src='data:image/png;base64,{encoded}'
                    width='500'
                >

            </div>
            """,
            unsafe_allow_html=True
        )

except FileNotFoundError:

    st.warning(
        "Logo not found. "
        "Place image.png inside assets/"
    )

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title(
    "📅 CPT Production Team Scheduler"
)

st.markdown(
    """
    Upload your:

    - Skills spreadsheet
    - Availability spreadsheet

    Supported formats:

    - CSV
    - XLSX
    - ODS
    """
)

# ---------------------------------------------------
# FILE UPLOADERS
# ---------------------------------------------------

skills_file = st.file_uploader(
    "Upload Skills File",
    type=[
        "csv",
        "xlsx",
        "ods"
    ]
)

availability_file = st.file_uploader(
    "Upload Availability File",
    type=[
        "csv",
        "xlsx",
        "ods"
    ]
)

# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------

if skills_file and availability_file:

    try:

        # ---------------------------------------------------
        # PROGRESS BAR
        # ---------------------------------------------------

        progress_bar = st.progress(0)

        status_text = st.empty()

        def update_progress(
            progress,
            message
        ):

            progress_bar.progress(
                min(progress, 1.0)
            )

            status_text.info(
                f"⚙️ {message}"
            )

        # ---------------------------------------------------
        # LOAD FILES
        # ---------------------------------------------------

        update_progress(
            0.05,
            "Loading spreadsheets..."
        )

        skills_df = load_dataframe(
            skills_file
        )

        availability_df = load_dataframe(
            availability_file
        )

        # ---------------------------------------------------
        # VALIDATION
        # ---------------------------------------------------

        required_skills_columns = [
            "Name"
        ]

        required_availability_columns = [
            "Name"
        ]

        missing_skills = [

            col for col in
            required_skills_columns

            if col not in skills_df.columns
        ]

        missing_availability = [

            col for col in
            required_availability_columns

            if col not in availability_df.columns
        ]

        if missing_skills:

            st.error(
                "Skills file missing columns: "
                + ", ".join(missing_skills)
            )

            st.stop()

        if missing_availability:

            st.error(
                "Availability file missing columns: "
                + ", ".join(missing_availability)
            )

            st.stop()

        # ---------------------------------------------------
        # GENERATE SCHEDULE
        # ---------------------------------------------------

        update_progress(
            0.15,
            "Optimizing schedule..."
        )

        schedule_result = generate_schedule(
            skills_df,
            availability_df,
            progress_callback=update_progress
        )

        # ---------------------------------------------------
        # BUILD EXCEL OUTPUT
        # ---------------------------------------------------

        update_progress(
            0.90,
            "Building Excel export..."
        )

        output = BytesIO()

        build_excel_output(
            schedule_result,
            output
        )

        # ---------------------------------------------------
        # BUILD METRICS
        # ---------------------------------------------------

        metrics = build_metrics(
            schedule_result
        )

        # ---------------------------------------------------
        # COMPLETE
        # ---------------------------------------------------

        progress_bar.progress(1.0)

        status_text.success(
            "✅ Schedule generation complete"
        )

        st.success(
            "✅ Schedule generated successfully"
        )

        # ---------------------------------------------------
        # METRICS
        # ---------------------------------------------------

        st.markdown(
            "## 📊 Schedule Metrics"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Coverage Rate",
            f"{metrics['coverage_rate']}%"
        )

        col2.metric(
            "Unfilled Roles",
            metrics["unfilled_roles"]
        )

        col3.metric(
            "Fairness Std Dev",
            metrics["fairness_std_dev"]
        )

        col4.metric(
            "Average Skill Score",
            metrics["avg_skill_score"]
        )

        # ---------------------------------------------------
        # SUMMARY TABLE
        # ---------------------------------------------------

        st.markdown(
            "## 📋 Assignment Summary"
        )

        summary_df = schedule_result[
            "summary"
        ]

        if not summary_df.empty:

            st.dataframe(
                summary_df,
                use_container_width=True
            )

        else:

            st.warning(
                "No summary data generated."
            )

        # ---------------------------------------------------
        # ASSIGNMENTS TABLE
        # ---------------------------------------------------

        st.markdown(
            "## 🗓 Full Assignments"
        )

        assignments_df = schedule_result[
            "assignments"
        ]

        if not assignments_df.empty:

            st.dataframe(
                assignments_df,
                use_container_width=True
            )

        else:

            st.warning(
                "No assignments generated."
            )

        # ---------------------------------------------------
        # DOWNLOAD BUTTON
        # ---------------------------------------------------

        st.download_button(

            label="📥 Download Excel Schedule",

            data=output.getvalue(),

            file_name=(
                "production_schedule.xlsx"
            ),

            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except Exception as e:

        st.error(
            "❌ Scheduler Error"
        )

        st.exception(e)
