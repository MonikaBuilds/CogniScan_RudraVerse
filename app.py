from __future__ import annotations

import tempfile
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.analyzer import analyze_screening
from src.sample_cases import SAMPLE_CASES


st.set_page_config(page_title="CogniScan", page_icon="C", layout="wide")


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
    }
    [data-testid="stHeader"] { background: transparent; border-bottom: none; }
    [data-testid="stToolbar"] { display: none; }
    .stApp { background: var(--paper); }
    .block-container { max-width: 1120px; padding-top: 2.4rem; padding-bottom: 2.8rem; }
    .hero {
        background: var(--panel);
        color: #f8f4ee;
        border-radius: 30px;
        padding: 2.4rem 2.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 22px 48px rgba(23, 23, 23, 0.14);
    }
    .hero * { color: #f8f4ee !important; }
    .eyebrow {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        opacity: 0.72;
        margin-bottom: 0.85rem;
    }
    .info-card {
        background: rgba(252, 250, 246, 0.94);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1.15rem 1.2rem;
    }
    .section-heading {
        margin: 0 0 1rem 0;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 2.05rem;
        line-height: 1.05;
        letter-spacing: -0.03em;
    }
    .output-shell {
        background: rgba(252, 250, 246, 0.72);
        border: 1px solid #e7dfd2;
        border-radius: 26px;
        padding: 1.15rem;
        margin-top: 0.4rem;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.9rem;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: rgba(252, 250, 246, 0.96);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        min-height: 126px;
    }
    .stat-label {
        color: var(--muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
    }
    .stat-value {
        color: var(--ink);
        font-size: 1.25rem;
        line-height: 1.12;
        font-family: Georgia, "Times New Roman", serif;
        word-break: break-word;
    }
    .stat-note {
        margin-top: 0.35rem;
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.35;
        word-break: break-word;
    }
    .summary-card {
        background: rgba(252, 250, 246, 0.96);
        border: 1px solid #eadbc8;
        border-radius: 22px;
        padding: 1rem 1.1rem;
        box-shadow: inset 4px 0 0 var(--accent);
    }
    .list-shell {
        background: rgba(252, 250, 246, 0.96);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1rem 1.05rem;
        height: 100%;
    }
    .list-item {
        padding: 0.85rem 0;
        border-top: 1px solid #ece5d9;
        color: var(--ink);
        line-height: 1.5;
        word-break: break-word;
    }
    .list-item:first-child {
        border-top: none;
        padding-top: 0;
    }
    .sample-case {
        background: rgba(252, 250, 246, 0.96);
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
        line-height: 1.2;
        word-break: break-word;
    }
    .sample-meta {
        color: var(--muted);
        font-size: 0.93rem;
        margin-bottom: 0.4rem;
        line-height: 1.45;
        word-break: break-word;
    }
    .cohort-legend {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }
    .legend-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        border: 1px solid var(--line);
        background: rgba(252, 250, 246, 0.96);
        color: var(--ink);
        font-size: 0.85rem;
    }
    .legend-dot {
        width: 0.72rem;
        height: 0.72rem;
        border-radius: 999px;
        display: inline-block;
    }
    .risk-badge {
        display: inline-block;
        margin-top: 0.8rem;
        padding: 0.34rem 0.72rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    @media (max-width: 900px) {
        .stats-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 640px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
    h1, h2, h3 { color: var(--ink) !important; font-family: Georgia, "Times New Roman", serif; }
    p, li, span, label, div { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .stSelectbox label, .stSlider label, .stTextArea label, .stFileUploader label, .stCaption { color: var(--ink) !important; }
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextArea textarea {
        background: rgba(252, 250, 246, 0.96) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
    }
    .stTextArea textarea::placeholder { color: var(--muted) !important; }
    .stSelectbox svg { fill: var(--muted) !important; color: var(--muted) !important; stroke: var(--muted) !important; }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[role="listbox"] div {
        background: var(--surface) !important;
        color: var(--ink) !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(252, 250, 246, 0.96) !important;
        border: 1px solid var(--line) !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        padding-left: 4.2rem !important;
        position: relative !important;
    }
    [data-testid="stFileUploaderDropzone"]::before {
        content: "?";
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
        font-size: 1.05rem;
        font-weight: 700;
    }
    [data-testid="stFileUploaderDropzone"] svg,
    [data-testid="stFileUploaderDropzone"] [data-testid="stFileUploaderDropzoneIcon"] { display: none !important; }
    [data-testid="stFileUploaderDropzone"] * { color: var(--ink) !important; }
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] span { color: var(--muted) !important; }
    [data-testid="stFileUploaderDropzone"] button,
    .stButton > button {
        background: var(--panel) !important;
        color: #f8f4ee !important;
        border: 1px solid var(--panel) !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        min-height: 50px !important;
    }
    .stButton > button:hover { background: var(--panel-soft) !important; border-color: var(--panel-soft) !important; }
    [data-testid="stTable"] { background: rgba(252, 250, 246, 0.96); border-radius: 16px; }
    div[data-testid="stTable"] table { background: rgba(252, 250, 246, 0.96) !important; }
    div[data-testid="stTable"] th, div[data-testid="stTable"] td { color: var(--ink) !important; border-color: #ece5d9 !important; }
    [data-testid="stVegaLiteChart"] { background: transparent !important; border: none !important; box-shadow: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">HC-02: AI-Based Early Cognitive Decline Detection System</div>
        <h1 style="margin:0;">CogniScan</h1>
        <p style="margin:12px 0 0 0; max-width:760px; font-size:1.03rem;">
            A speech-first screening prototype for early cognitive decline that combines transcript patterns,
            memory-task performance, and caregiver concern into an explainable review summary.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-card">
        <strong>Round 1 demo focus</strong><br>
        One working core functionality: analyze a short patient speech sample and return a structured, explainable screening summary.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

case_col, info_col = st.columns([1.05, 0.95], gap="large")
with case_col:
    selected_case_name = st.selectbox("Load a sample patient", [case["name"] for case in SAMPLE_CASES], index=1)
    selected_case = get_case(selected_case_name)
with info_col:
    st.caption("Use a sample case for the demo, or edit the values manually before running the screening.")

left, right = st.columns([1.18, 0.82], gap="large")
with left:
    st.subheader("Input")
    age = st.slider("Patient age", 50, 90, selected_case["age"])
    memory_task_score = st.slider("Memory task score (out of 10)", 0, 10, selected_case["memory_task_score"])
    caregiver_concern = st.slider("Caregiver concern level", 1, 5, selected_case["caregiver_concern"])
    uploaded_audio = st.file_uploader("Optional speech sample (.wav)", type=["wav"])
    transcript = st.text_area("Transcript / patient response", value=selected_case["transcript"], height=220)
    analyze = st.button("Analyze Screening", type="primary", use_container_width=True)

with right:
    st.subheader("What the engine looks at")
    st.markdown(
        """
        - transcript structure and lexical variety
        - hesitation, repetition, and confusion markers
        - short memory-task performance
        - caregiver concern level
        - optional speaking pace from audio duration
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
    st.markdown('<div class="section-heading">Output</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="output-shell">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Risk Score</div>
                    <div class="stat-value">{result['risk_score']} / 100</div>
                    <div class="stat-note">Composite screening score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Risk Band</div>
                    <div class="stat-value">{result['category']}</div>
                    <div class="stat-note">Overall screening category</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Sample Quality</div>
                    <div class="stat-value">{result['sample_quality']}%</div>
                    <div class="stat-note">Input richness for this sample</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Top Driver</div>
                    <div class="stat-value">{result['top_drivers'][0]}</div>
                    <div class="stat-note">Strongest signal in this screening</div>
                </div>
            </div>
            <div class="summary-card" style="border-color:{accent}; background:{background};">
                <div style="font-size:1.03rem; font-weight:700; color:{accent}; margin-bottom:0.45rem;">Screening Summary</div>
                <div style="color:#1f1d1a; font-size:1.02rem; margin-bottom:0.55rem; line-height:1.45;">{result['narrative']}</div>
                <div style="color:#3f3a34; margin-bottom:0.42rem; line-height:1.5;">{result['recommendation']}</div>
                <div style="color:#6f695f; line-height:1.5;">Top drivers: {', '.join(result['top_drivers'])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    insight_left, insight_right = st.columns([1, 1], gap="large")
    with insight_left:
        st.markdown("### Observed Markers")
        markers_markup = "".join(f'<div class="list-item">{marker}</div>' for marker in result["observed_markers"])
        st.markdown(f'<div class="list-shell">{markers_markup}</div>', unsafe_allow_html=True)
    with insight_right:
        st.markdown("### Suggested Next Steps")
        with st.container(border=True):
            for index, step in enumerate(result["next_steps"], 1):
                row_left, row_right = st.columns([0.12, 0.88], gap="small")
                with row_left:
                    st.markdown(
                        f"""
                        <div style="
                            width:2.1rem;
                            height:2.1rem;
                            border-radius:999px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            background:#efe6d8;
                            color:#8c4a24;
                            font-weight:700;
                            margin-top:0.15rem;
                        ">{index}</div>
                        """,
                        unsafe_allow_html=True,
                    )
                with row_right:
                    st.write(step)

    detail_col, viz_col = st.columns([0.92, 1.08], gap="large")
    with detail_col:
        st.markdown("### Feature Summary")
        feature_df = pd.DataFrame(
            [{"Feature": str(key), "Value": str(value)} for key, value in result["feature_summary"].items()]
        )
        st.dataframe(feature_df, use_container_width=True, hide_index=True)

    with viz_col:
        st.markdown("### Relative Feature Impact")
        explanation_df = pd.DataFrame(
            [
                {"Model Signal": key.replace("_", " ").title(), "Relative Risk": round(value, 3)}
                for key, value in result["feature_scores"].items()
            ]
        ).sort_values("Relative Risk", ascending=False)
        explanation_df["Label"] = explanation_df["Relative Risk"].map(lambda value: f"{value:.2f}")

        chart = alt.Chart(explanation_df).mark_bar(
            cornerRadiusTopRight=8,
            cornerRadiusBottomRight=8,
            color="#c96f3b",
            size=24,
        ).encode(
            y=alt.Y("Model Signal:N", sort="-x", axis=alt.Axis(title=None, labelLimit=220)),
            x=alt.X(
                "Relative Risk:Q",
                axis=alt.Axis(title=None, labels=False, ticks=False, grid=True),
                scale=alt.Scale(domain=[0, 1]),
            ),
            tooltip=["Model Signal", "Relative Risk"],
        )
        labels = alt.Chart(explanation_df).mark_text(
            align="left",
            baseline="middle",
            dx=8,
            color="#7a3f1d",
            fontWeight=700,
        ).encode(
            y=alt.Y("Model Signal:N", sort="-x"),
            x=alt.X("Relative Risk:Q"),
            text="Label:N",
        )
        final_chart = (
            (chart + labels)
            .properties(height=340, padding={"left": 24, "right": 28, "top": 10, "bottom": 8})
            .configure_view(strokeWidth=0)
            .configure_axis(
                labelColor="#6f695f",
                titleColor="#6f695f",
                gridColor="#ede6da",
                domain=False,
                ticks=False,
            )
        )
        st.altair_chart(final_chart, use_container_width=True)

st.write("")
st.subheader("Sample Cohort")
cohort_rows = []
for case in SAMPLE_CASES:
    result = analyze_screening(
        transcript=case["transcript"],
        age=case["age"],
        memory_task_score=case["memory_task_score"],
        caregiver_concern=case["caregiver_concern"],
    )
    cohort_rows.append(
        {
            "Patient": case["name"],
            "Risk Score": result["risk_score"],
            "Risk Band": result["category"],
            "Memory Score": case["memory_task_score"],
            "Concern": case["caregiver_concern"],
        }
    )

cohort_df = pd.DataFrame(cohort_rows).sort_values("Risk Score", ascending=False)
cohort_df["Score Label"] = cohort_df["Risk Score"].map(lambda value: f"{value:.1f}")
cohort_base = alt.Chart(cohort_df).encode(
    y=alt.Y("Patient:N", sort="-x", axis=alt.Axis(title=None, labelLimit=160)),
    x=alt.X(
        "Risk Score:Q",
        scale=alt.Scale(domain=[0, 100]),
        axis=alt.Axis(title="Risk score", grid=True, values=[0, 20, 40, 60, 80, 100]),
    ),
    color=alt.Color(
        "Risk Band:N",
        scale=alt.Scale(
            domain=["Low Risk", "Moderate Risk", "High Risk"],
            range=["#4f9f75", "#c96f3b", "#b42318"],
        ),
        legend=None,
    ),
    tooltip=["Patient", "Risk Score", "Risk Band"],
)
cohort_bars = cohort_base.mark_bar(cornerRadiusTopRight=10, cornerRadiusBottomRight=10, size=28)
cohort_labels = cohort_base.mark_text(
    align="left",
    baseline="middle",
    dx=8,
    color="#5b3420",
    fontWeight=700,
).encode(text="Score Label:N")
cohort_chart = (
    (cohort_bars + cohort_labels)
    .properties(height=190, padding={"left": 8, "right": 28, "top": 8, "bottom": 6})
    .configure_view(strokeWidth=0)
    .configure_axis(
        labelColor="#6f695f",
        titleColor="#6f695f",
        gridColor="#ede6da",
        domain=False,
        tickColor="#d8d0c2",
    )
)

cohort_left, cohort_right = st.columns([1.15, 0.85], gap="large")
with cohort_left:
    st.markdown(
        """
        <div class="cohort-legend">
            <span class="legend-pill"><span class="legend-dot" style="background:#4f9f75;"></span>Low Risk</span>
            <span class="legend-pill"><span class="legend-dot" style="background:#c96f3b;"></span>Moderate Risk</span>
            <span class="legend-pill"><span class="legend-dot" style="background:#b42318;"></span>High Risk</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.altair_chart(cohort_chart, use_container_width=True)
with cohort_right:
    for row in cohort_rows:
        badge_bg, badge_fg = badge_for(row["Risk Band"])
        st.markdown(
            f"""
            <div class="sample-case" style="margin-bottom:0.9rem;">
                <h4>{row['Patient']}</h4>
                <div class="sample-meta">Risk score: {row['Risk Score']}</div>
                <div class="sample-meta">Memory score: {row['Memory Score']} / 10</div>
                <div class="sample-meta">Caregiver concern: {row['Concern']} / 5</div>
                <span class="risk-badge" style="background:{badge_bg}; color:{badge_fg};">{row['Risk Band']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
