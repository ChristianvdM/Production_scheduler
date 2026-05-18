import streamlit as st
import pandas as pd
from io import BytesIO
import base64

from scheduler.loaders import load_dataframe
from scheduler.optimizer import generate_schedule
from scheduler.exports import build_excel_output
from scheduler.metrics import build_metrics

st.set_page_config(
    page_title="CPT Production Team Scheduler",
    layout="wide"
)

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
    </style>
    """,
    unsafe_allow_html=True
)

# Logo
try:
    with open("assets/image.png", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

        st.markdown(
            f"""
            <div style='text-align: center;'>
                <img src='data:image/png;base64,{encoded}' width='600'>
            </div>
            """,
            unsafe_allow_html=True
        )

except FileNotFoundError:
    st.warning("Logo not found")

st.title("📅 CPT Production Team Scheduler")

st.markdown(
    """
Upload:

- Skills File (.ods / .xlsx / .csv)
- Availability File (.ods / .xlsx / .csv)
"""
)

skills_file = st.file_uploader(
    "Upload Skills File",
    type=["csv", "xlsx", "ods"]
)

availability_file = st.file_uploader(
    "Upload Availability File",
    type=["csv", "xlsx", "ods"]
)

if skills_file and availability_file:

    with st.spinner("Generating optimized schedule..."):

        skills_df = load_dataframe(skills_file)
        availability_df = load_dataframe(availability_file)

        schedule_result = generate_schedule(
            skills_df,
            availability_df
        )

        output = BytesIO()

        build_excel_output(
            schedule_result,
            output
        )

        metrics = build_metrics(schedule_result)

    st.success("✅ Schedule generated successfully")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Coverage Rate",
        f"{metrics['coverage_rate']}%"
    )

    col2.metric(
        "Unfilled Roles",
        metrics['unfilled_roles']
    )

    col3.metric(
        "Fairness Std Dev",
        metrics['fairness_std_dev']
    )

    col4.metric(
        "Average Skill Score",
        metrics['avg_skill_score']
    )

    st.markdown("## Assignment Summary")
    st.dataframe(schedule_result['summary'])

    st.markdown("## Schedule Preview")
    st.dataframe(schedule_result['assignments'].head(50))

    st.download_button(
        "📥 Download Schedule",
        data=output.getvalue(),
        file_name="production_schedule.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
