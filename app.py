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


def badge_for(category: str) -> tuple[str, str]:
    if category == "High Risk":
        return "#fef3f2", "#b42318"
    if category == "Moderate Risk":
        return "#fff7ed", "#b54708"
    return "#ecfdf3", "#027a48"


st.markdown(
    """
    <style>
    :root {
        --paper: #f7f4ef;
        --surface: #fcfaf6;
        --ink: #1f1d1a;
        --muted: #6f695f;
        --line: #d8d0c2;
        --panel: #171717;
        --panel-soft: #242321;
        --accent: #c96f3b;
        --accent-soft: #f3e5d8;
    }
    [data-testid="stHeader"] {
        background: transparent;
        border-bottom: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    .stApp {
        background: var(--paper);
    }
    .block-container {
        max-width: 1120px;
        padding-top: 2.4rem;
        padding-bottom: 2.5rem;
    }
    .hero {
        background: var(--panel);
        color: #f8f4ee;
        border-radius: 28px;
        padding: 36px 38px;
        margin-bottom: 1.2rem;
        box-shadow: 0 20px 50px rgba(23, 23, 23, 0.14);
    }
    .hero h1, .hero p, .hero div {
        color: #f8f4ee !important;
    }
    .eyebrow {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        opacity: 0.72;
        margin-bottom: 0.8rem;
    }
    .subtle-card {
        background: rgba(253, 251, 247, 0.82);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 20px 20px;
        color: var(--ink) !important;
    }
    .subtle-card strong,
    .subtle-card div,
    .subtle-card p {
        color: var(--ink) !important;
    }
    .result-card {
        border-radius: 22px;
        padding: 20px 20px;
        border: 1px solid var(--line);
        background: var(--surface);
    }
    .sample-case {
        background: rgba(253, 251, 247, 0.92);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem;
        height: 100%;
    }
    .sample-case h4 {
        margin: 0 0 0.55rem 0;
        color: var(--ink);
        font-size: 1.05rem;
        font-family: Georgia, "Times New Roman", serif;
    }
    .sample-meta {
        color: var(--muted);
        font-size: 0.93rem;
        margin-bottom: 0.3rem;
    }
    .risk-badge {
        display: inline-block;
        margin-top: 0.85rem;
        padding: 0.34rem 0.7rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }
    .small-note {
        color: var(--muted);
        font-size: 0.96rem;
    }
    .stSelectbox label,
    .stSlider label,
    .stTextArea label,
    .stFileUploader label,
    .stMarkdown,
    .stCaption {
        color: var(--ink) !important;
    }
    h1, h2, h3 {
        color: var(--ink) !important;
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: -0.02em;
    }
    p, li, span, label, div {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(253, 251, 247, 0.92) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
        min-height: 48px !important;
    }
    .stSelectbox svg {
        fill: var(--muted) !important;
        color: var(--muted) !important;
        stroke: var(--muted) !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[role="listbox"] div {
        background: var(--surface) !important;
        color: var(--ink) !important;
    }
    .stTextArea textarea {
        background: rgba(253, 251, 247, 0.96) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 16px !important;
    }
    .stTextArea textarea::placeholder {
        color: var(--muted) !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(253, 251, 247, 0.96) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        box-shadow: none !important;
        border-radius: 16px !important;
        padding-top: 0.45rem !important;
        padding-bottom: 0.45rem !important;
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
        background: #efe6d8;
        border: 1px solid #dec8ad;
        color: var(--accent);
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
        color: var(--ink) !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: var(--muted) !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: var(--panel) !important;
        color: #f8f4ee !important;
        border: 1px solid var(--panel) !important;
        border-radius: 12px !important;
    }
    .stButton > button {
        background: var(--panel) !important;
        color: #f8f4ee !important;
        border: 1px solid var(--panel) !important;
        border-radius: 14px !important;
        min-height: 50px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background: var(--panel-soft) !important;
        border-color: var(--panel-soft) !important;
    }
    [data-testid="stMetric"] {
        background: rgba(253, 251, 247, 0.9);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: var(--ink) !important;
    }
    [data-testid="stTable"] {
        background: rgba(253, 251, 247, 0.96);
        border-radius: 16px;
    }
    div[data-testid="stTable"] table {
        background: rgba(253, 251, 247, 0.96) !important;
    }
    div[data-testid="stTable"] th,
    div[data-testid="stTable"] td {
        color: var(--ink) !important;
        border-color: #ece5d9 !important;
    }
    [data-testid="stVegaLiteChart"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
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
        explanation_df["Label"] = explanation_df["Relative Risk"].map(lambda value: f"{value:.2f}")
        chart = (
            alt.Chart(explanation_df)
            .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8, color="#c96f3b", size=24)
            .encode(
                y=alt.Y("Model Signal:N", sort="-x", axis=alt.Axis(title=None, labelLimit=220)),
                x=alt.X(
                    "Relative Risk:Q",
                    axis=alt.Axis(title=None, labels=False, ticks=False, grid=True),
                    scale=alt.Scale(domain=[0, 1]),
                ),
                tooltip=["Model Signal", "Relative Risk"],
            )
            .properties(height=320)
        )
        labels = (
            alt.Chart(explanation_df)
            .mark_text(align="left", baseline="middle", dx=8, color="#7a3f1d", fontWeight=700)
            .encode(
                y=alt.Y("Model Signal:N", sort="-x"),
                x=alt.X("Relative Risk:Q"),
                text="Label:N",
            )
        )
        chart = (
            (chart + labels)
            .properties(padding={"left": 24, "right": 28, "top": 10, "bottom": 10})
            .configure_view(strokeWidth=0)
            .configure_axis(
                labelColor="#6f695f",
                titleColor="#6f695f",
                gridColor="#ede6da",
                domain=False,
                ticks=False,
            )
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
        badge_bg, badge_fg = badge_for(row["Risk Band"])
        st.markdown(
            f"""
            <div class="sample-case">
                <h4>{row['Patient']}</h4>
                <div class="sample-meta">Age: {row['Age']}</div>
                <div class="sample-meta">Memory score: {row['Memory Score']} / 10</div>
                <div class="sample-meta">Caregiver concern: {row['Caregiver Concern']} / 5</div>
                <div class="sample-meta">Risk score: {row['Risk Score']}</div>
                <span class="risk-badge" style="background:{badge_bg}; color:{badge_fg};">{row['Risk Band']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
