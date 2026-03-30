# CogniScan

CogniScan is a Streamlit prototype for the Nakshatra problem statement:
`HC-02: AI-Based Early Cognitive Decline Detection System`.

The current build focuses on one clear Round 1 workflow:

- load or enter a short patient speech sample
- add memory-task score and caregiver concern
- generate an explainable screening summary
- compare the result against a small sample cohort

## Project Structure

- `app.py`
  Main Streamlit application
- `src/analyzer.py`
  Screening logic and scoring helpers
- `src/sample_cases.py`
  Demo patient cases used in the UI
- `docs/architecture.md`
  High-level product and system explanation
- `docs/team-guide.md`
  Setup and run guide for teammates

## Quick Start

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Current Demo Flow

1. Load `Ramesh Patil` from the sample selector.
2. Run the screening.
3. Show the risk score, risk band, observed markers, and next steps.
4. Use the cohort section to compare low, moderate, and high-risk cases.

## Architecture Overview

```mermaid
flowchart LR
    A[Patient Speech Sample] --> D[Feature Extraction]
    B[Memory Task Score] --> D
    C[Caregiver Concern] --> D
    E[Optional WAV Duration] --> D

    D --> F[Screening Engine]
    F --> G[Risk Score]
    F --> H[Risk Band]
    F --> I[Observed Markers]
    F --> J[Top Drivers]
    F --> K[Suggested Next Steps]

    G --> L[Clinician or Reviewer Dashboard]
    H --> L
    I --> L
    J --> L
    K --> L
```

## Prototype Component View

```mermaid
flowchart TD
    UI[Streamlit App UI]
    CASES[sample_cases.py]
    ANALYZER[analyzer.py]
    OUTPUT[Summary and Visualization Layer]

    CASES --> UI
    UI --> ANALYZER
    ANALYZER --> OUTPUT
    OUTPUT --> UI
```

## Future-State Architecture

```mermaid
flowchart LR
    A[Patient Audio] --> B[Speech-to-Text]
    A --> C[Speech Pacing and Pause Analysis]
    D[Memory Tasks] --> E[Task Scoring]
    F[Caregiver Inputs] --> G[Concern Scoring]
    H[Facial or Behavioral Cues] --> I[Multimodal Marker Extraction]

    B --> J[Multimodal Risk Engine]
    C --> J
    E --> J
    G --> J
    I --> J

    J --> K[Screening Summary]
    J --> L[Risk Trend Tracking]
    J --> M[Clinician Review Queue]
    J --> N[Caregiver Alerts]
```

## Note

This prototype should be presented as a screening-support system for early review, not as a medical diagnosis tool.
