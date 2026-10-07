# Lumivise — AI-Powered Data Analytics

A Streamlit application for exploring CSV/Excel datasets, creating interactive charts, generating Gemini-assisted interpretations, and exporting PDF reports.

## What is included

- Safe cleaning removes empty and duplicate records without blanket missing-value imputation.
- Automatic reports cover categories, distributions, relationships, time trends, hierarchies, and geography when suitable columns exist.
- Visual Explorer supports chart selection, aggregation, filters, and a session canvas.
- Local report history supports separate uploaded datasets.
- ReportLab produces downloadable reports.

## Getting started

Use a compatible Python environment:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

On Windows activate with `.venv\Scripts\activate`. Set `GEMINI_API_KEY` in the environment or in an untracked `.streamlit/secrets.toml` file. Upload a CSV/XLSX dataset and use Auto Report or Visual Explorer.

## Repository guide

- `README.md`
- `chats/`
- `fevicon.png`
- `main.py`
- `requirements.txt`
- `source.zip`
- `uploads/`

## Limitations and reproducibility

The code selects `gemini-1.5-flash`; verify that this model is available to your API account and update `MODEL_NAME` if needed. AI requests transmit column context and computed analytical findings to Google. Uploaded files and report history are stored in local `uploads/` and `chats/`; this is not an authenticated multi-user storage design. AI interpretations require review. Dependencies are unpinned, and the app has not been end-to-end tested during this documentation pass.
