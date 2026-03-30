# Team Guide

## What this project is

CogniScan is a Streamlit-based prototype for early cognitive screening support.

It does not require a backend service or database. Everything runs locally from the app and the files in `src/`.

## Requirements

- Python 3.11 or newer recommended
- `pip`

## Setup

From the project root:

```powershell
pip install -r requirements.txt
```

## Run the app

```powershell
streamlit run app.py
```

If Streamlit says the default port is already in use, run:

```powershell
streamlit run app.py --server.port 8502
```

## Files teammates will most likely edit

- `app.py`
  UI, layout, and visualization
- `src/analyzer.py`
  Risk scoring logic and summary outputs
- `src/sample_cases.py`
  Demo patient cases
- `docs/ppt-content.md`
  Presentation content
- `docs/demo-script.md`
  Demo narration outline

## Demo recommendation

Use the sample patient `Ramesh Patil` for the main live walkthrough.

Why:

- the result is moderate risk, which gives enough signal to talk through
- the explanation section becomes more meaningful
- it feels realistic and balanced in a demo

## Troubleshooting

### App opens but styling looks old

Stop any old Streamlit process and run the app again. Browser tabs can also keep an older running instance open.

### Port already in use

Run on another port:

```powershell
streamlit run app.py --server.port 8502
```

### Dependencies missing

Reinstall:

```powershell
pip install -r requirements.txt
```

## Team workflow suggestion

1. Keep UI edits in `app.py`.
2. Keep logic edits in `src/analyzer.py`.
3. Update sample data in `src/sample_cases.py`.
4. If demo flow changes, update `docs/demo-script.md` and `docs/ppt-content.md`.
