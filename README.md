# CogniScan Intelligence Suite

CogniScan is a polished Round 1 prototype for `HC-02: AI-Based Early Cognitive Decline Detection System`.

It is built as a speech-first clinical intelligence experience with:

- a premium product-style UI
- explainable screening logic
- a synthetic patient cohort
- a deployment roadmap
- ready-to-use hackathon submission content

## What is included

- `app.py`
  Streamlit app with executive overview, screening studio, cohort analytics, operations story, and submission kit
- `src/analyzer.py`
  Explainable risk-scoring engine using transcript, caregiver, memory, and optional WAV pacing signals
- `src/sample_cases.py`
  Synthetic demo patients for low, moderate, and high-risk walkthroughs
- `docs/architecture.md`
  Product and system architecture narrative
- `docs/demo-script.md`
  Demo flow for judges and video recording
- `docs/ppt-content.md`
  Slide-by-slide content for your presentation

## Local setup

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Recommended presentation flow

1. Start on the executive overview to frame the problem.
2. Open the screening studio and run one patient case live.
3. Show the explainability chart and recommendation.
4. Switch to the cohort lab to show case separation.
5. End on the operations and submission tabs to prove scale and product thinking.

## Positioning for Round 1

This is not a diagnosis engine. Present it as an early-warning screening assistant for clinicians and caregivers that helps identify patients who should receive deeper evaluation sooner.
