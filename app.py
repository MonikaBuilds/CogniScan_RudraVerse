from __future__ import annotations

import tempfile
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.analyzer import analyze_screening
from src.sample_cases import SAMPLE_CASES


st.set_page_config(
    page_title="CogniScan",
    page_icon="🧠",
    layout="wide",
)


def get_case(case_name: str) -> dict:
    return next(case for case in SAMPLE_CASES if case["name"] == case_name)


def tone_for(category: str) -> tuple[str, str]:
    if category == "High Risk":
        return "#fff1f1", "#b42318"
    if category == "Moderate Risk":
        return "#fff7ed", "#b54708"
    return "#f0fdf4", "#027a48"


st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        background: transparent;
        border-bottom: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    .stApp {
        background: #f8fafc;
    }
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .hero {
        background: #0f172a;
        color: white;
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 1rem;
    }
    .hero h1, .hero p, .hero div {
        color: white !important;
    }
    .eyebrow {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        opacity: 0.8;
        margin-bottom: 0.6rem;
    }
    .subtle-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px 18px;
        color: #0f172a !important;
    }
    .subtle-card strong,
    .subtle-card div,
    .subtle-card p {
        color: #0f172a !important;
    }
    .result-card {
        border-radius: 18px;
        padding: 18px 18px;
        border: 1px solid #e2e8f0;
    }
    .small-note {
        color: #475569;
        font-size: 0.95rem;
    }
    .stSelectbox label,
    .stSlider label,
    .stTextArea label,
    .stFileUploader label,
    .stMarkdown,
    .stCaption {
        color: #0f172a !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stSelectbox svg {
        fill: #475569 !important;
        color: #475569 !important;
        stroke: #475569 !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[role="listbox"] div {
        background: #ffffff !important;
        color: #0f172a !important;
    }
    .stTextArea textarea {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stTextArea textarea::placeholder {
        color: #64748b !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: none !important;
        border-radius: 12px !important;
        padding-top: 0.25rem !important;
        padding-bottom: 0.25rem !important;
        position: relative !important;
        padding-left: 4.25rem !important;
    }
    [data-testid="stFileUploaderDropzone"]::before {
        content: "↑";
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        width: 2rem;
        height: 2rem;
        border-radius: 999px;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #2563eb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 700;
        line-height: 1;
        z-index: 2;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #0f172a !important;
        fill: currentColor !important;
    }
    [data-testid="stFileUploaderDropzone"] svg {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] [data-testid="stFileUploaderDropzoneIcon"] {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] section {
        border: none !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #0f172a !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: #475569 !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #0f172a !important;
    }
    .stButton > button {
        background: #ef4444 !important;
        color: #ffffff !important;
        border: 1px solid #ef4444 !important;
    }
    .stButton > button:hover {
        background: #dc2626 !important;
        border-color: #dc2626 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">HC-02: AI-Based Early Cognitive Decline Detection System</div>
        <h1 style="margin:0;">CogniScan</h1>
        <p style="margin:12px 0 0 0; max-width:760px;">
            Speech-based screening support for early cognitive decline using transcript patterns,
            memory-task score, and caregiver concern.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtle-card">
        <strong>Round 1 demo scope</strong><br>
        This prototype demonstrates one working core functionality: analyzing a short patient speech sample
        and generating an explainable screening summary.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

case_col, info_col = st.columns([1.1, 0.9], gap="large")

with case_col:
    selected_case_name = st.selectbox(
        "Load a sample patient",
        [case["name"] for case in SAMPLE_CASES],
        index=1,
    )
    selected_case = get_case(selected_case_name)

with info_col:
    st.caption("You can use a sample case for the demo or edit the values manually below.")

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("Input")

    age = st.slider("Patient age", 50, 90, selected_case["age"])
    memory_task_score = st.slider("Memory task score (out of 10)", 0, 10, selected_case["memory_task_score"])
    caregiver_concern = st.slider("Caregiver concern level", 1, 5, selected_case["caregiver_concern"])
    uploaded_audio = st.file_uploader("Optional speech sample (.wav)", type=["wav"])
    transcript = st.text_area(
        "Transcript / patient response",
        value=selected_case["transcript"],
        height=220,
    )
    analyze = st.button("Analyze", type="primary", use_container_width=True)

with right:
    st.subheader("What This Uses")
    st.markdown(
        """
        - Speech transcript structure
        - Hesitation and confusion markers
        - Short memory-task score
        - Caregiver concern level
        - Optional speech pacing from audio duration
        """
    )


if analyze:
    audio_path = None
    if uploaded_audio is not None:
        temp_dir = Path(tempfile.gettempdir())
        audio_path = str(temp_dir / uploaded_audio.name)
        with open(audio_path, "wb") as audio_file:
            audio_file.write(uploaded_audio.getbuffer())

    result = analyze_screening(
        transcript=transcript,
        age=age,
        memory_task_score=memory_task_score,
        caregiver_concern=caregiver_concern,
        audio_path=audio_path,
    )

    background, accent = tone_for(result["category"])

    st.write("")
    st.subheader("Output")
    metric_a, metric_b, metric_c = st.columns(3, gap="large")
    metric_a.metric("Risk Score", f"{result['risk_score']} / 100")
    metric_b.metric("Risk Band", result["category"])
    metric_c.metric("Top Driver", result["top_drivers"][0])

    st.markdown(
        f"""
        <div class="result-card" style="background:{background}; border-color:{accent};">
            <div style="font-size:1.05rem; font-weight:700; color:{accent}; margin-bottom:8px;">Screening Summary</div>
            <div style="color:#0f172a; margin-bottom:8px;">{result["recommendation"]}</div>
            <div class="small-note">Key drivers: {", ".join(result["top_drivers"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    details_col, explain_col = st.columns([0.95, 1.05], gap="large")

    with details_col:
        feature_rows = [(str(key), str(value)) for key, value in result["feature_summary"].items()]
        st.markdown("#### Feature Summary")
        feature_df = pd.DataFrame(feature_rows, columns=["Feature", "Value"])
        st.table(feature_df)

    with explain_col:
        explanation_df = pd.DataFrame(
            [
                {"Model Signal": key.replace("_", " ").title(), "Relative Risk": round(value, 3)}
                for key, value in result["feature_scores"].items()
            ]
        ).sort_values("Relative Risk", ascending=False)
        st.markdown("#### Relative Feature Impact")
        chart = (
            alt.Chart(explanation_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color="#2563eb")
            .encode(
                x=alt.X("Model Signal:N", sort=None, axis=alt.Axis(title=None, labelAngle=-40, labelLimit=180)),
                y=alt.Y("Relative Risk:Q", axis=alt.Axis(title="Risk Weight"), scale=alt.Scale(domain=[0, 1])),
                tooltip=["Model Signal", "Relative Risk"],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)


st.write("")
st.subheader("Sample Cases")
sample_rows = []
for case in SAMPLE_CASES:
    result = analyze_screening(
        transcript=case["transcript"],
        age=case["age"],
        memory_task_score=case["memory_task_score"],
        caregiver_concern=case["caregiver_concern"],
    )
    sample_rows.append(
        {
            "Patient": case["name"],
            "Age": case["age"],
            "Memory Score": case["memory_task_score"],
            "Caregiver Concern": case["caregiver_concern"],
            "Risk Score": result["risk_score"],
            "Risk Band": result["category"],
        }
    )

sample_columns = st.columns(3, gap="large")
for column, row in zip(sample_columns, sample_rows):
    with column:
        with st.container(border=True):
            st.markdown(f"**{row['Patient']}**")
            st.caption(
                f"Age: {row['Age']} | Memory: {row['Memory Score']}/10 | Caregiver concern: {row['Caregiver Concern']}/5"
            )
            st.write(f"Risk score: {row['Risk Score']}")
            if row["Risk Band"] == "Low Risk":
                st.success(row["Risk Band"])
            elif row["Risk Band"] == "Moderate Risk":
                st.warning(row["Risk Band"])
            else:
                st.error(row["Risk Band"])
