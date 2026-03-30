from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analyzer import analyze_screening
from src.sample_cases import SAMPLE_CASES


st.set_page_config(
    page_title="CogniScan Intelligence Suite",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_case(case_name: str) -> dict:
    return next(case for case in SAMPLE_CASES if case["name"] == case_name)


def render_metric_card(label: str, value: str, caption: str, tone: str = "default") -> None:
    st.markdown(
        f"""
        <div class="metric-card {tone}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_cohort_dataframe() -> pd.DataFrame:
    rows = []
    for case in SAMPLE_CASES:
        result = analyze_screening(
            transcript=case["transcript"],
            age=case["age"],
            memory_task_score=case["memory_task_score"],
            caregiver_concern=case["caregiver_concern"],
        )
        rows.append(
            {
                "Patient": case["name"],
                "Age": case["age"],
                "Memory Score": case["memory_task_score"],
                "Caregiver Concern": case["caregiver_concern"],
                "Risk Score": result["risk_score"],
                "Risk Band": result["category"],
                "Primary Drivers": ", ".join(result["top_drivers"][:2]),
                "Recommendation": result["recommendation"],
            }
        )
    return pd.DataFrame(rows).sort_values("Risk Score", ascending=False)


def category_tone(category: str) -> str:
    mapping = {
        "High Risk": "high",
        "Moderate Risk": "moderate",
        "Low Risk": "low",
    }
    return mapping.get(category, "default")


st.markdown(
    """
    <style>
    :root {
        --bg: #f3efe6;
        --panel: #fffdfa;
        --ink: #172121;
        --muted: #4b5a5c;
        --line: #d5d0c4;
        --navy: #19323c;
        --teal: #1f7a8c;
        --sand: #f4b860;
        --rose: #bc4b51;
        --sage: #7c9a92;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(244, 184, 96, 0.18), transparent 30%),
            radial-gradient(circle at top right, rgba(31, 122, 140, 0.10), transparent 28%),
            linear-gradient(180deg, #f7f4ec 0%, #f1ede3 100%);
        color: var(--ink);
    }
    .block-container {
        max-width: 1320px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #19323c 0%, #244b57 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * {
        color: #f8faf7;
    }
    h1, h2, h3 {
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: 0.01em;
    }
    .hero-shell {
        padding: 2rem;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 28px;
        background:
            linear-gradient(120deg, rgba(25, 50, 60, 0.96) 0%, rgba(31, 122, 140, 0.92) 52%, rgba(124, 154, 146, 0.92) 100%);
        box-shadow: 0 24px 60px rgba(25, 50, 60, 0.18);
        color: white;
        overflow: hidden;
        position: relative;
    }
    .hero-shell:before {
        content: "";
        position: absolute;
        inset: auto -40px -60px auto;
        width: 220px;
        height: 220px;
        background: rgba(244, 184, 96, 0.18);
        border-radius: 50%;
        filter: blur(2px);
    }
    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 0.75rem;
        opacity: 0.8;
        margin-bottom: 0.8rem;
    }
    .hero-grid {
        display: grid;
        grid-template-columns: 1.6fr 1fr;
        gap: 1rem;
        align-items: end;
    }
    .hero-title {
        font-size: 3rem;
        line-height: 1;
        margin: 0;
    }
    .hero-copy {
        font-size: 1.02rem;
        max-width: 700px;
        margin-top: 0.9rem;
        color: rgba(255,255,255,0.88);
    }
    .chip-row {
        margin-top: 1rem;
    }
    .chip {
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.55rem;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.18);
        background: rgba(255,255,255,0.12);
        font-size: 0.84rem;
    }
    .panel {
        border-radius: 24px;
        padding: 1.1rem 1.2rem;
        background: rgba(255,255,255,0.76);
        border: 1px solid rgba(213, 208, 196, 0.8);
        box-shadow: 0 18px 40px rgba(39, 53, 57, 0.08);
        backdrop-filter: blur(4px);
    }
    .metric-card {
        border-radius: 20px;
        padding: 1rem 1rem 0.95rem 1rem;
        background: #fffdf9;
        border: 1px solid #dfd8c8;
        min-height: 132px;
    }
    .metric-card.low { border-color: rgba(124,154,146,0.55); background: #f7fbf9; }
    .metric-card.moderate { border-color: rgba(244,184,96,0.7); background: #fff8ee; }
    .metric-card.high { border-color: rgba(188,75,81,0.6); background: #fff3f3; }
    .metric-label {
        color: var(--muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.55rem;
    }
    .metric-value {
        font-size: 2rem;
        line-height: 1;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 0.4rem;
    }
    .metric-caption {
        font-size: 0.92rem;
        color: var(--muted);
    }
    .info-strip {
        border-left: 4px solid var(--teal);
        background: rgba(31, 122, 140, 0.08);
        padding: 0.85rem 1rem;
        border-radius: 12px;
        color: var(--navy);
    }
    .workflow-step {
        border-top: 1px solid #dfd8c8;
        padding-top: 0.85rem;
        margin-top: 0.85rem;
    }
    .story-card {
        height: 100%;
        border-radius: 22px;
        padding: 1rem 1.1rem;
        background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(248,245,237,0.96));
        border: 1px solid #dfd8c8;
    }
    .story-kicker {
        color: #7b5e2d;
        text-transform: uppercase;
        font-size: 0.76rem;
        letter-spacing: 0.16em;
    }
    .divider-title {
        margin-top: 0.25rem;
        margin-bottom: 0.35rem;
        font-size: 1.4rem;
    }
    .sidebar-note {
        padding: 0.9rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## CogniScan")
    st.caption("Clinical Intelligence Suite")
    st.write(
        "Speech-led cognitive triage built for low-resource environments, caregiver visibility, and clinician escalation."
    )

    selected_case_name = st.selectbox("Load quick case", [case["name"] for case in SAMPLE_CASES], index=1)
    selected_case = load_case(selected_case_name)

    st.markdown("### Deployment Pillars")
    st.write("- 2-minute screening workflow")
    st.write("- Explainable risk scoring")
    st.write("- Caregiver escalation logic")
    st.write("- Offline-first deployment path")

    st.markdown(
        """
        <div class="sidebar-note">
            <strong>Pitch line</strong><br/>
            CogniScan turns short patient speech into an explainable early-warning signal for cognitive decline.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Current Demo Case")
    st.write(f"Name: {selected_case['name']}")
    st.write(f"Age: {selected_case['age']}")
    st.write(f"Memory task: {selected_case['memory_task_score']} / 10")
    st.write(f"Caregiver concern: {selected_case['caregiver_concern']} / 5")


st.markdown(
    """
    <div class="hero-shell">
        <div class="hero-grid">
            <div>
                <div class="eyebrow">Healthcare AI / Early Screening / Triage Intelligence</div>
                <h1 class="hero-title">CogniScan Intelligence Suite</h1>
                <div class="hero-copy">
                    An industry-style cognitive screening experience that combines patient speech, structured memory checks,
                    and caregiver context into an explainable triage recommendation.
                </div>
                <div class="chip-row">
                    <span class="chip">Speech Analytics</span>
                    <span class="chip">Clinical Explainability</span>
                    <span class="chip">Caregiver Alerts</span>
                    <span class="chip">Low-Resource Deployment</span>
                </div>
            </div>
            <div class="panel" style="background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.16);">
                <div class="eyebrow" style="color:rgba(255,255,255,0.72);margin-bottom:0.45rem;">Why judges care</div>
                <div style="font-size:1.6rem;font-weight:700;line-height:1.1;">High-clarity AI prototype with a believable deployment path</div>
                <div style="margin-top:0.7rem;color:rgba(255,255,255,0.85);font-size:0.98rem;">
                    It shows one real working module today and a strong roadmap for a multimodal healthcare platform tomorrow.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


overview_tab, screening_tab, cohort_tab, ops_tab, submission_tab = st.tabs(
    ["Executive Overview", "Screening Studio", "Cohort Lab", "Operations Layer", "Submission Kit"]
)


with overview_tab:
    top_left, top_mid, top_right = st.columns(3, gap="large")
    with top_left:
        render_metric_card("Use Case", "Early Screening", "Designed for first-line triage in clinics and at-home monitoring.")
    with top_mid:
        render_metric_card("Core Signal", "Speech + Memory", "Low-friction data collection that works without expensive hardware.")
    with top_right:
        render_metric_card("Deployment Style", "Offline-Friendly", "Suitable for low-resource pilots with caregiver integration.")

    st.markdown("")
    story_left, story_right = st.columns([1.2, 1], gap="large")

    with story_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Product Thesis")
        st.write(
            "Cognitive decline often surfaces first in subtle speech changes, memory slips, and caregiver observations. "
            "CogniScan packages those early warning signs into a triage workflow that is simple enough for frontline use and "
            "clear enough for clinicians to trust."
        )
        st.markdown('<div class="info-strip">Core prototype promise: one short interaction becomes a measurable, explainable risk estimate.</div>', unsafe_allow_html=True)
        st.markdown('<div class="workflow-step"><strong>Step 1</strong> Capture a short patient narration or response.</div>', unsafe_allow_html=True)
        st.markdown('<div class="workflow-step"><strong>Step 2</strong> Combine transcript features with memory score and caregiver concern.</div>', unsafe_allow_html=True)
        st.markdown('<div class="workflow-step"><strong>Step 3</strong> Produce a risk band, key drivers, and recommended escalation path.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with story_right:
        left_story, right_story = st.columns(2, gap="medium")
        with left_story:
            st.markdown(
                """
                <div class="story-card">
                    <div class="story-kicker">Differentiator</div>
                    <div class="divider-title">Explainable AI</div>
                    <p>Instead of a black-box output, the demo shows what drove the score: memory performance, hesitation, confusion, repetition, and caregiver concern.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with right_story:
            st.markdown(
                """
                <div class="story-card">
                    <div class="story-kicker">Scale Path</div>
                    <div class="divider-title">Multimodal Future</div>
                    <p>The speech-first module is immediately demoable, while the platform roadmap expands into facial cues, cognitive tasks, and longitudinal patient tracking.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")
    market_left, market_right = st.columns([0.9, 1.1], gap="large")
    with market_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Why This Wins Round 1")
        st.write("- Strong healthcare impact with visible human value")
        st.write("- No hardware dependency for the prototype demo")
        st.write("- Product-grade UI instead of a bare utility screen")
        st.write("- Clear jump from MVP to deployment roadmap")
        st.markdown("</div>", unsafe_allow_html=True)
    with market_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Recommended Demo Flow")
        st.write("1. Start here and state the problem in one sentence.")
        st.write("2. Open Screening Studio and analyze a patient sample.")
        st.write("3. Show the explanation chart and recommendation output.")
        st.write("4. Switch to Cohort Lab to prove the model separates cases.")
        st.write("5. End with Submission Kit to present architecture and roadmap.")
        st.markdown("</div>", unsafe_allow_html=True)


with screening_tab:
    screen_left, screen_right = st.columns([1.2, 0.8], gap="large")

    with screen_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Clinical Screening Console")

        use_sample = st.toggle("Preload sidebar sample case", value=True)
        default_transcript = selected_case["transcript"] if use_sample else ""
        default_age = selected_case["age"] if use_sample else 68
        default_memory = selected_case["memory_task_score"] if use_sample else 6
        default_concern = selected_case["caregiver_concern"] if use_sample else 3

        age = st.slider("Patient age", 50, 90, default_age)
        memory_task_score = st.slider("Memory task score (out of 10)", 0, 10, default_memory)
        caregiver_concern = st.slider("Caregiver concern level", 1, 5, default_concern)
        uploaded_audio = st.file_uploader("Optional speech sample (.wav)", type=["wav"])

        transcript = st.text_area(
            "Transcript / observation text",
            height=240,
            value=default_transcript,
            placeholder="Paste a patient speech sample, interview response, or observed narration here.",
        )
        analyze = st.button("Generate Clinical Summary", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with screen_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Screening Notes")
        st.write(
            "This prototype focuses on one core function: early cognitive risk triage from a short speech-led interaction."
        )
        st.write(
            "It is intentionally scoped for Round 1 so your team can show a working experience instead of an overpromised medical stack."
        )
        st.markdown("### Input Signals")
        st.write("- Patient age")
        st.write("- Immediate memory task performance")
        st.write("- Caregiver concern level")
        st.write("- Transcript semantics and structure")
        st.write("- Optional speaking-rate estimate from WAV duration")
        st.markdown("</div>", unsafe_allow_html=True)

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

        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            render_metric_card("Risk Score", f"{result['risk_score']} / 100", "Composite triage estimate.", category_tone(result["category"]))
        with c2:
            render_metric_card("Risk Band", result["category"], "Decision-ready category for the next action.", category_tone(result["category"]))
        with c3:
            render_metric_card("Top Driver", result["top_drivers"][0], "Most influential model signal in this screening.", category_tone(result["category"]))

        summary_col, explain_col = st.columns([0.92, 1.08], gap="large")
        with summary_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("### Clinical Summary")
            st.write(result["recommendation"])
            st.write("Key drivers: " + ", ".join(result["top_drivers"]))
            features_df = pd.DataFrame(
                [{"Feature": key, "Value": value} for key, value in result["feature_summary"].items()]
            )
            st.dataframe(features_df, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with explain_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("### Explainability View")
            explanation_df = pd.DataFrame(
                [
                    {"Model Signal": key.replace("_", " ").title(), "Relative Risk": round(value, 3)}
                    for key, value in result["feature_scores"].items()
                ]
            ).sort_values("Relative Risk", ascending=False)
            st.bar_chart(explanation_df.set_index("Model Signal"))
            st.markdown("</div>", unsafe_allow_html=True)


with cohort_tab:
    cohort_df = build_cohort_dataframe()
    cohort_left, cohort_right = st.columns([1.1, 0.9], gap="large")

    with cohort_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Synthetic Cohort Dashboard")
        st.caption("Use this tab in the demo to show that the risk engine differentiates patient profiles.")
        st.dataframe(cohort_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with cohort_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Case Spotlight")
        spotlight_name = st.selectbox("Choose a patient", cohort_df["Patient"].tolist(), key="cohort_patient")
        spotlight = load_case(spotlight_name)
        spotlight_result = analyze_screening(
            transcript=spotlight["transcript"],
            age=spotlight["age"],
            memory_task_score=spotlight["memory_task_score"],
            caregiver_concern=spotlight["caregiver_concern"],
        )
        st.write(f"Risk band: {spotlight_result['category']}")
        st.write(f"Risk score: {spotlight_result['risk_score']}")
        st.write("Top drivers: " + ", ".join(spotlight_result["top_drivers"]))
        st.text_area("Transcript", spotlight["transcript"], height=190)
        st.markdown("</div>", unsafe_allow_html=True)

    chart_left, chart_right = st.columns(2, gap="large")
    with chart_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Risk Score Comparison")
        st.bar_chart(cohort_df.set_index("Patient")[["Risk Score"]])
        st.markdown("</div>", unsafe_allow_html=True)
    with chart_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Memory Score vs Risk")
        memory_chart = cohort_df[["Patient", "Memory Score", "Risk Score"]].set_index("Patient")
        st.line_chart(memory_chart)
        st.markdown("</div>", unsafe_allow_html=True)


with ops_tab:
    ops_left, ops_right = st.columns([1.05, 0.95], gap="large")
    with ops_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Deployment Architecture")
        st.code(
            "Patient Speech / Caregiver Inputs / Memory Check\n"
            "        |\n"
            "Feature Extraction Layer\n"
            "        |\n"
            "Explainable Risk Engine\n"
            "        |\n"
            "Clinician Dashboard + Caregiver Alerts + Repeat Screening Records",
            language="text",
        )
        st.write(
            "For a real deployment, the current app becomes the triage console while a backend service stores repeat visits, "
            "trendlines, and escalation history."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with ops_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Industrial Positioning")
        st.write("- Primary users: clinics, neurologists, geriatrics teams, home-care providers")
        st.write("- Secondary users: family caregivers and health workers")
        st.write("- Deployment mode: tablet or desktop app with offline-first sync")
        st.write("- Value proposition: faster screening, earlier referral, better follow-up visibility")
        st.markdown("</div>", unsafe_allow_html=True)

    roadmap_a, roadmap_b, roadmap_c = st.columns(3, gap="large")
    with roadmap_a:
        render_metric_card("Phase 1", "Speech-First MVP", "Current demoable module with explainable risk logic.")
    with roadmap_b:
        render_metric_card("Phase 2", "Multimodal Upgrade", "Add Whisper transcription, facial cues, and guided tasks.")
    with roadmap_c:
        render_metric_card("Phase 3", "Clinical Platform", "Longitudinal monitoring, doctor notes, and caregiver notifications.")


with submission_tab:
    sub_left, sub_right = st.columns([1, 1], gap="large")

    with sub_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### PPT Slide Blueprint")
        st.write("1. Problem: early cognitive decline is caught too late")
        st.write("2. Why now: aging population and limited specialist access")
        st.write("3. Solution: CogniScan as a speech-first AI triage assistant")
        st.write("4. Prototype flow: transcript + memory + caregiver concern -> risk score")
        st.write("5. Demo screenshots: screening studio and cohort dashboard")
        st.write("6. Impact: earlier referral and better caregiver visibility")
        st.write("7. Roadmap: multimodal expansion and longitudinal records")
        st.write("8. Ask: shortlist us for Round 2")
        st.markdown("</div>", unsafe_allow_html=True)

    with sub_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Video Script Spine")
        st.write("Opening: cognitive decline is subtle, but early intervention changes outcomes.")
        st.write("Problem: current screening is delayed, inconsistent, and specialist-dependent.")
        st.write("Demo: show one patient speech sample and the explainable result.")
        st.write("Differentiator: low-resource, interpretable, caregiver-aware.")
        st.write("Close: CogniScan is the first module of a full multimodal detection suite.")
        st.markdown("</div>", unsafe_allow_html=True)

    final_left, final_mid, final_right = st.columns(3, gap="large")
    with final_left:
        render_metric_card("Core Build", "Working Prototype", "Ready to show live during selection review.")
    with final_mid:
        render_metric_card("Submission Mode", "Round 1 Ready", "Supports PPT, recording, and quick demo walkthroughs.")
    with final_right:
        render_metric_card("Strategic Story", "Healthcare + AI", "Balances feasibility, impact, and judge appeal.")
