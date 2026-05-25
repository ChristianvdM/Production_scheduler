import streamlit as st
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

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# LOGO
# ---------------------------------------------------

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
            <div style='text-align:center;'>

                <img
                    src='data:image/png;base64,{encoded}'
                    width='500'
                >

            </div>
            """,
            unsafe_allow_html=True
        )

except:
    pass

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title(
    "📅 CPT Production Team Scheduler"
)

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

        progress_bar = st.progress(0)

        status = st.empty()

        def update_progress(
            progress,
            message
        ):

            progress_bar.progress(
                progress
            )

            status.info(
                f"⚙️ {message}"
            )

        # ---------------------------------------------------
        # LOAD FILES
        # ---------------------------------------------------

        skills_df = load_dataframe(
            skills_file
        )

        availability_df = load_dataframe(
            availability_file
        )

        # ---------------------------------------------------
        # GENERATE
        # ---------------------------------------------------

        schedule_result = generate_schedule(
            skills_df,
            availability_df,
            progress_callback=update_progress
        )

        # ---------------------------------------------------
        # EXPORT
        # ---------------------------------------------------

        output = BytesIO()

        build_excel_output(
            schedule_result,
            output
        )

        metrics = build_metrics(
            schedule_result
        )

        progress_bar.progress(1.0)

        status.success(
            "✅ Schedule complete"
        )

        # ---------------------------------------------------
        # METRICS
        # ---------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Coverage",
            f"{metrics['coverage_rate']}%"
        )

        col2.metric(
            "Unfilled",
            metrics["unfilled_roles"]
        )

        col3.metric(
            "Fairness",
            metrics["fairness_std_dev"]
        )

        col4.metric(
            "Skill",
            metrics["avg_skill_score"]
        )

        # ---------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------

        st.markdown(
            "## Summary"
        )

        st.dataframe(
            schedule_result["summary"],
            width="stretch"
        )

        # ---------------------------------------------------
        # ASSIGNMENTS
        # ---------------------------------------------------

        st.markdown(
            "## Assignments"
        )

        st.dataframe(
            schedule_result["assignments"],
            width="stretch"
        )

        # ---------------------------------------------------
        # DOWNLOAD
        # ---------------------------------------------------

        st.download_button(

            label="📥 Download Schedule",

            data=output.getvalue(),

            file_name=(
                "production_schedule.xlsx"
            ),

            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )

    except Exception as e:

        st.error(
            "❌ Scheduler Error"
        )

        st.exception(e)
