import os
import json
import uuid
import re
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai
from google.genai import types

# =========================================================
# CONFIG
# =========================================================
MODEL_NAME = "gemini-1.5-flash"
APP_TITLE = "Lumivise - Illuminate, Visualize, Summarize."
CHATS_DIR = "chats"
UPLOADS_DIR = "uploads"

os.makedirs(CHATS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="fevicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM DASHBOARD UI THEME
# =========================================================
def apply_premium_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root { --text-main:#172033; --text-muted:#64748B; --accent:#4F7DF3; --border:rgba(148,163,184,.22); --shadow:0 18px 45px rgba(15,23,42,.08); --shadow-soft:0 8px 24px rgba(15,23,42,.06); }
    html, body, [class*="css"] { font-family:'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stApp { background: radial-gradient(circle at top left, rgba(79,125,243,.16), transparent 30%), radial-gradient(circle at top right, rgba(124,58,237,.10), transparent 28%), linear-gradient(180deg,#F8FAFC 0%,#F3F6FB 48%,#EEF4FF 100%); color:var(--text-main); }
    .stApp::before { content:""; position:fixed; inset:0; pointer-events:none; background-image:linear-gradient(rgba(79,125,243,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(79,125,243,.045) 1px,transparent 1px); background-size:38px 38px; mask-image:linear-gradient(to bottom,rgba(0,0,0,.55),transparent 70%); }
    .block-container { max-width:1420px; padding-top:1.2rem; padding-bottom:3rem; animation:fadeInUp .45s ease both; }
    @keyframes fadeInUp { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
    section[data-testid="stSidebar"] { background:rgba(255,255,255,.84); backdrop-filter:blur(18px); border-right:1px solid var(--border); box-shadow:12px 0 36px rgba(15,23,42,.045); }
    section[data-testid="stSidebar"] * { color:var(--text-main); }
    h1,h2,h3 { color:var(--text-main); letter-spacing:-.03em; } h1{font-weight:800;} h2{font-weight:750;margin-top:1.2rem;} h3{font-weight:700;}
    .premium-hero { position:relative; overflow:hidden; padding:26px 30px; border-radius:28px; background:linear-gradient(135deg,rgba(255,255,255,.95),rgba(239,246,255,.84)); border:1px solid rgba(255,255,255,.84); box-shadow:var(--shadow); margin-bottom:1.4rem; }
    .premium-hero::after { content:""; position:absolute; width:280px; height:280px; right:-90px; top:-120px; background:radial-gradient(circle,rgba(79,125,243,.20),transparent 65%); animation:floatBlob 9s ease-in-out infinite; }
    @keyframes floatBlob { 0%,100%{transform:translate(0,0) scale(1);} 50%{transform:translate(-18px,20px) scale(1.08);} }
    .premium-eyebrow { display:inline-flex; padding:7px 12px; border-radius:999px; background:#EEF4FF; color:#3655D4; font-size:13px; font-weight:800; margin-bottom:10px; }
    .premium-title { font-size:40px; line-height:1.05; margin:0; font-weight:850; color:var(--text-main); }
    .premium-subtitle { max-width:760px; margin-top:10px; color:var(--text-muted); font-size:16px; line-height:1.55; }
    .soft-card { background:rgba(255,255,255,.86); border:1px solid rgba(255,255,255,.82); border-radius:22px; padding:18px 20px; box-shadow:var(--shadow-soft); backdrop-filter:blur(14px); }
    .kpi-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:12px 0 20px 0; }
    .kpi-card { background:linear-gradient(180deg,rgba(255,255,255,.96),rgba(248,250,252,.94)); border:1px solid rgba(226,232,240,.9); border-radius:22px; padding:18px; box-shadow:var(--shadow-soft); position:relative; overflow:hidden; }
    .kpi-card::after { content:""; position:absolute; width:74px; height:74px; border-radius:50%; right:-26px; top:-26px; background:rgba(79,125,243,.11); }
    .kpi-label { color:var(--text-muted); font-size:13px; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }
    .kpi-value { margin-top:8px; font-size:30px; line-height:1; font-weight:850; color:var(--text-main); }
    .kpi-note { margin-top:8px; color:var(--text-muted); font-size:13px; }
    div[data-testid="metric-container"] { background:linear-gradient(180deg,rgba(255,255,255,.96),rgba(248,250,252,.94)); border:1px solid rgba(226,232,240,.9); border-radius:20px; padding:16px; box-shadow:var(--shadow-soft); }
    .stButton>button {
        background:rgba(255,255,255,.92);
        color:#172033;
        border:2px solid rgba(79,125,243,.78);
        border-radius:14px;
        padding:.55rem 1rem;
        font-weight:800;
        box-shadow:0 8px 20px rgba(15,23,42,.06);
        transition:transform .18s ease, box-shadow .18s ease, background .18s ease, color .18s ease, border-color .18s ease;
    }
    .stButton>button:hover {
        background:linear-gradient(135deg,#4F7DF3,#6D5DF7);
        color:white;
        border-color:#4F7DF3;
        transform:translateY(-1px);
        box-shadow:0 14px 30px rgba(79,125,243,.28);
    }
    .stButton>button:active { transform:scale(.98); }
    div[data-testid="stFileUploader"] { background:rgba(255,255,255,.76); border:2px dashed rgba(79,125,243,.42); border-radius:22px; padding:12px; transition:border-color .18s ease, box-shadow .18s ease, background .18s ease; }
    div[data-testid="stFileUploader"]:hover { border-color:#4F7DF3; box-shadow:0 10px 26px rgba(79,125,243,.12); background:rgba(255,255,255,.90); }
    .report-info-card {
        background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(246,249,255,.92));
        border:1px solid rgba(203,213,225,.75);
        border-radius:26px;
        padding:20px 22px;
        box-shadow:0 18px 45px rgba(15,23,42,.08);
        backdrop-filter:blur(16px);
        position:sticky;
        top:18px;
        max-width:100%;
    }
    .report-info-head { display:flex; align-items:center; gap:12px; margin-bottom:16px; }
    .report-info-icon { width:42px; height:42px; border-radius:14px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#EAF1FF,#F4F0FF); box-shadow:inset 0 0 0 1px rgba(79,125,243,.16); font-size:22px; }
    .report-info-title { font-size:20px; font-weight:850; color:#172033; letter-spacing:-.03em; line-height:1.1; }
    .report-info-subtitle { font-size:12px; color:#64748B; margin-top:3px; font-weight:650; }
    .report-info-list { display:flex; flex-direction:column; gap:10px; }
    .report-info-row { display:grid; grid-template-columns:112px minmax(0,1fr); align-items:center; gap:12px; padding:11px 12px; background:rgba(248,250,252,.82); border:1px solid rgba(226,232,240,.82); border-radius:16px; }
    .report-info-label { color:#64748B; font-size:12px; font-weight:850; text-transform:uppercase; letter-spacing:.065em; white-space:nowrap; }
    .report-info-value { color:#172033; font-size:13.5px; font-weight:800; text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .report-info-value:hover { white-space:normal; word-break:break-word; }

    .sidebar-report-card {
        margin-top:14px;
        background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(246,249,255,.92));
        border:1px solid rgba(203,213,225,.75);
        border-radius:18px;
        padding:14px;
        box-shadow:0 10px 26px rgba(15,23,42,.07);
    }
    .sidebar-report-head { display:flex; align-items:center; gap:9px; margin-bottom:12px; }
    .sidebar-report-icon { width:34px; height:34px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:#EEF4FF; font-size:18px; }
    .sidebar-report-title { font-size:16px; font-weight:850; color:#172033; line-height:1.05; }
    .sidebar-report-subtitle { font-size:11px; font-weight:650; color:#64748B; margin-top:2px; }
    .sidebar-info-row { padding:9px 0; border-top:1px solid rgba(226,232,240,.9); }
    .sidebar-info-label { font-size:10.5px; color:#64748B; font-weight:850; text-transform:uppercase; letter-spacing:.07em; margin-bottom:3px; }
    .sidebar-info-value { font-size:12.5px; color:#172033; font-weight:800; word-break:break-word; line-height:1.35; }
    .stTabs [data-baseweb="tab-list"] { gap:10px; background:rgba(255,255,255,.60); padding:8px; border-radius:18px; border:1px solid rgba(226,232,240,.8); box-shadow:var(--shadow-soft); }
    .stTabs [data-baseweb="tab"] { height:44px; padding:0 20px; border-radius:14px; color:var(--text-muted); font-weight:750; }
    .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#EEF4FF,#F4F0FF); color:#3655D4; box-shadow:inset 0 0 0 1px rgba(79,125,243,.14); }
    div[data-testid="stDataFrame"], .stDataFrame { border-radius:18px; overflow:hidden; box-shadow:var(--shadow-soft); border:1px solid rgba(226,232,240,.85); }
    div[data-testid="stPlotlyChart"] { background:rgba(255,255,255,.86); border:1px solid rgba(226,232,240,.85); border-radius:22px; padding:12px; box-shadow:var(--shadow-soft); min-height:460px; overflow:visible!important; }
    div[data-testid="stPlotlyChart"] .js-plotly-plot { border:0!important; box-shadow:none!important; overflow:visible!important; min-height:420px!important; }
    div[data-testid="stPlotlyChart"] .plot-container, div[data-testid="stPlotlyChart"] .svg-container { min-height:420px!important; overflow:visible!important; }
    hr { border:none; height:1px; background:linear-gradient(90deg,transparent,rgba(148,163,184,.35),transparent); margin:1.4rem 0; }
    label { color:#334155!important; font-weight:700!important; }
    .chart-explain { background:linear-gradient(135deg,rgba(255,255,255,.92),rgba(239,246,255,.82)); border:1px solid rgba(191,219,254,.72); border-left:5px solid #4F7DF3; padding:14px 16px; margin-top:8px; margin-bottom:24px; border-radius:16px; box-shadow:0 8px 20px rgba(15,23,42,.045); }
    .chart-explain b { color:#1E293B; } .chart-explain span { font-size:14.5px; color:#475569; line-height:1.55; }
    @media(max-width:900px){ .kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));} .premium-title{font-size:30px;} }


    /* PREMIUM INPUTS, DROPDOWNS, MULTISELECTS */
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] {
        background-color: rgba(255,255,255,.94) !important;
        border: 1.5px solid #DDE6F3 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(15,23,42,.035) !important;
        transition: border-color .18s ease, box-shadow .18s ease, background-color .18s ease;
    }

    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="base-input"]:hover,
    div[data-baseweb="input"]:hover {
        border-color: #B7C5FF !important;
        background-color: #FAFCFF !important;
        box-shadow: 0 8px 18px rgba(79,125,243,.08) !important;
    }

    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="input"]:focus-within {
        border-color: #8EA2FF !important;
        box-shadow: 0 0 0 3px rgba(142,162,255,.18), 0 8px 18px rgba(79,125,243,.08) !important;
        background-color: #FFFFFF !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="input"] input {
        color: #334155 !important;
        font-weight: 600 !important;
    }

    ul[role="listbox"] {
        border: 1px solid #DDE6F3 !important;
        border-radius: 14px !important;
        box-shadow: 0 18px 42px rgba(15,23,42,.12) !important;
        overflow: hidden !important;
    }

    li[role="option"] {
        color: #334155 !important;
        font-weight: 600 !important;
        padding: 10px 12px !important;
    }

    li[role="option"]:hover {
        background-color: #F1F5FF !important;
        color: #273A8A !important;
    }

    li[aria-selected="true"] {
        background-color: #EAF0FF !important;
        color: #3655D4 !important;
    }

    /* Radio options in sidebar */
    div[role="radiogroup"] label {
        background: rgba(255,255,255,.70);
        border: 1px solid rgba(226,232,240,.88);
        border-radius: 12px;
        padding: 7px 10px;
        margin-bottom: 6px;
        transition: all .18s ease;
    }

    div[role="radiogroup"] label:hover {
        background: #F1F5FF;
        border-color: #B7C5FF;
    }

    /* Date input popover / general popovers */
    div[data-baseweb="popover"] {
        border-radius: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_premium_hero():
    st.markdown(f"""
    <div class="premium-hero">
        <div class="premium-eyebrow">Premium Analytics Workspace</div>
        <h1 class="premium-title">{APP_TITLE}</h1>
    </div>
    """, unsafe_allow_html=True)


def render_info_card(title: str, value: str, note: str = ""):
    st.markdown(f"""
    <div class="soft-card">
        <div style="font-size:13px;font-weight:800;color:#64748B;text-transform:uppercase;letter-spacing:.06em;">{title}</div>
        <div style="font-size:17px;font-weight:750;color:#172033;margin-top:7px;word-break:break-word;">{value}</div>
        <div style="font-size:13px;color:#64748B;margin-top:6px;">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(items: List[Tuple[str, str, str]]):
    html = '<div class="kpi-grid">'
    for label, value, note in items:
        html += f'''<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>'''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def apply_plotly_theme(fig):
    fig.update_layout(
        template="plotly_white",
        height=430,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, Arial, sans-serif", color="#1E293B", size=13),
        title=dict(font=dict(size=19, color="#172033"), x=0.02, xanchor="left"),
        margin=dict(l=55, r=35, t=68, b=60),
        legend=dict(
            bgcolor="rgba(255,255,255,0.72)",
            bordercolor="rgba(226,232,240,0.9)",
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.16)", zeroline=False, automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.16)", zeroline=False, automargin=True)
    return fig

def render_premium_chart(fig, *args, **kwargs):
    fig = apply_plotly_theme(fig)
    kwargs.setdefault("use_container_width", True)
    kwargs.setdefault("config", {"displaylogo": False, "responsive": True})
    return st.plotly_chart(fig, *args, **kwargs)


apply_premium_theme()
render_premium_hero()

st.warning(
    "For best visualization results, upload a pre-cleaned dataset. "
    "Lumivise will detect columns and generate suitable charts automatically, "
    "but it will not over-clean your data or blindly change correct data types."
)


# =========================================================
# MODEL - GEMINI CLOUD LLM
# =========================================================
@st.cache_resource
def load_llm():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("GEMINI_API_KEY is missing. Add it to .streamlit/secrets.toml or Streamlit Cloud secrets.")
        st.stop()

    return genai.Client(api_key=api_key)


def ask_gemini(prompt: str) -> str:
    client = load_llm()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=2600,
        ),
    )
    return response.text if hasattr(response, "text") else str(response)
# =========================================================
# GENERIC HELPERS
# =========================================================
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-. ]", "_", name)
    return name.strip().replace(" ", "_")


def shorten(text: str, max_len: int = 24) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def chat_file_path(chat_id: str) -> str:
    return os.path.join(CHATS_DIR, f"{chat_id}.json")


def upload_file_path(chat_id: str, original_name: str) -> str:
    return os.path.join(UPLOADS_DIR, f"{chat_id}__{sanitize_filename(original_name)}")


# =========================================================
# CHAT STORAGE
# =========================================================
def default_chat(title: str = "New Chat") -> dict:
    chat_id = str(uuid.uuid4())
    return {
        "chat_id": chat_id,
        "title": title,
        "created_at": now_str(),
        "updated_at": now_str(),
        "dataset_name": None,
        "dataset_path": None,
    }


def save_chat(chat: dict):
    chat["updated_at"] = now_str()
    with open(chat_file_path(chat["chat_id"]), "w", encoding="utf-8") as f:
        json.dump(chat, f, indent=2, ensure_ascii=False)


def load_chat(chat_id: str) -> dict:
    with open(chat_file_path(chat_id), "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_chats() -> List[dict]:
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(CHATS_DIR, filename), "r", encoding="utf-8") as f:
                    chats.append(json.load(f))
            except Exception:
                pass
    chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return chats


def create_new_chat(title: str = "Chat:") -> dict:
    chat = default_chat(title)
    save_chat(chat)
    return chat


def rename_chat(chat_id: str, new_title: str):
    chat = load_chat(chat_id)
    if new_title.strip():
        chat["title"] = new_title.strip()
        save_chat(chat)


def delete_chat(chat_id: str):
    try:
        chat = load_chat(chat_id)
        dataset_path = chat.get("dataset_path")
        if dataset_path and os.path.exists(dataset_path):
            os.remove(dataset_path)
    except Exception:
        pass

    path = chat_file_path(chat_id)
    if os.path.exists(path):
        os.remove(path)


def update_chat_dataset(chat: dict, uploaded_file):
    destination = upload_file_path(chat["chat_id"], uploaded_file.name)
    with open(destination, "wb") as f:
        f.write(uploaded_file.getbuffer())

    chat["dataset_name"] = uploaded_file.name
    chat["dataset_path"] = destination

    # Automatically use the uploaded dataset name as the report/chat name.
    chat["title"] = uploaded_file.name

    save_chat(chat)
    return chat


# =========================================================
# DATA HELPERS
# =========================================================
def load_dataframe_from_path(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset file not found: {path}")

    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path)

    raise ValueError("Only CSV and XLSX files are supported.")


def basic_safe_cleaning(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Apply only safe, non-destructive cleaning.

    This does NOT fill missing values and does NOT force/change correct data types.
    It only removes duplicate rows, fully empty rows/columns, and cleans column names
    so chart generation is safer.
    """
    cleaned = df.copy()

    before_rows = len(cleaned)
    before_cols = len(cleaned.columns)
    duplicate_count = int(cleaned.duplicated().sum())

    cleaned = cleaned.drop_duplicates()
    after_dedup_rows = len(cleaned)

    cleaned = cleaned.dropna(axis=0, how="all")
    after_empty_rows_removed = len(cleaned)

    cleaned = cleaned.dropna(axis=1, how="all")

    cleaned.columns = (
        cleaned.columns
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace("-", "_", regex=False)
    )

    report = {
        "raw_rows": before_rows,
        "raw_columns": before_cols,
        "duplicates_removed": duplicate_count,
        "empty_rows_removed": after_dedup_rows - after_empty_rows_removed,
        "empty_columns_removed": before_cols - len(cleaned.columns),
        "cleaned_rows": len(cleaned),
        "cleaned_columns": len(cleaned.columns),
        "missing_values_remaining": int(cleaned.isna().sum().sum()),
    }

    return cleaned, report


def try_convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    for col in df_copy.columns:
        if df_copy[col].dtype == "object":
            sample = df_copy[col].dropna().astype(str).head(20)
            if len(sample) == 0:
                continue

            parsed = 0
            for val in sample:
                try:
                    pd.to_datetime(val, errors="coerce", format="mixed")
                    parsed += 1
                except Exception:
                    pass

            if parsed >= max(3, int(len(sample) * 0.6)):
                try:
                    df_copy[col] = pd.to_datetime(df_copy[col], errors="coerce", format="mixed")
                except Exception:
                    pass

    return df_copy


def detect_column_types(df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    categorical_cols = [c for c in df.columns if c not in numeric_cols and c not in datetime_cols]
    return numeric_cols, datetime_cols, categorical_cols


def find_geo_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    result = {
        "country": None,
        "state": None,
        "city": None,
        "lat": None,
        "lon": None,
    }

    for col in df.columns:
        col_l = col.lower()
        if result["lat"] is None and ("latitude" in col_l or col_l == "lat"):
            result["lat"] = col
        if result["lon"] is None and ("longitude" in col_l or col_l == "lon" or col_l == "lng"):
            result["lon"] = col
        if result["country"] is None and "country" in col_l:
            result["country"] = col
        if result["state"] is None and "state" in col_l:
            result["state"] = col
        if result["city"] is None and "city" in col_l:
            result["city"] = col

    return result


def prepare_scatter_geo_dataframe(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    size_col: Optional[str] = None,
) -> Tuple[pd.DataFrame, Optional[str]]:
    """Make Plotly scatter_geo safe by removing invalid coordinates and marker sizes.

    Plotly crashes when marker size contains NaN, negative, or infinite values.
    This helper keeps the original dataframe untouched and creates a safe copy only for maps.
    """
    temp_df = df.copy()

    temp_df[lat_col] = pd.to_numeric(temp_df[lat_col], errors="coerce")
    temp_df[lon_col] = pd.to_numeric(temp_df[lon_col], errors="coerce")

    temp_df = temp_df.dropna(subset=[lat_col, lon_col])
    temp_df = temp_df[
        temp_df[lat_col].between(-90, 90) &
        temp_df[lon_col].between(-180, 180)
    ]

    safe_size_col = None
    if size_col and size_col in temp_df.columns:
        temp_df["_safe_marker_size"] = pd.to_numeric(temp_df[size_col], errors="coerce")
        temp_df["_safe_marker_size"] = temp_df["_safe_marker_size"].replace([float("inf"), float("-inf")], pd.NA)
        temp_df["_safe_marker_size"] = temp_df["_safe_marker_size"].fillna(0).clip(lower=0)

        if temp_df["_safe_marker_size"].sum() > 0:
            safe_size_col = "_safe_marker_size"

    return temp_df, safe_size_col


def choose_best_category_columns(df: pd.DataFrame, max_cols: int = 3) -> List[str]:
    _, _, categorical_cols = detect_column_types(df)

    ranked = []
    for col in categorical_cols:
        nunique = df[col].nunique(dropna=True)
        if 2 <= nunique <= 20:
            ranked.append((nunique, col))

    ranked.sort(key=lambda x: x[0])
    return [col for _, col in ranked[:max_cols]]


def choose_best_numeric_columns(df: pd.DataFrame, max_cols: int = 4) -> List[str]:
    numeric_cols, _, _ = detect_column_types(df)
    good = []
    for col in numeric_cols:
        non_null = df[col].dropna()
        if len(non_null) > 0:
            good.append(col)
    return good[:max_cols]


def choose_best_datetime_column(df: pd.DataFrame) -> Optional[str]:
    _, datetime_cols, _ = detect_column_types(df)
    return datetime_cols[0] if datetime_cols else None


def format_chart_name(chart_type: str) -> str:
    names = {
        "bar": "Bar Chart",
        "stacked_bar": "Stacked Bar Chart",
        "line": "Line Chart",
        "area": "Area Chart",
        "pie": "Pie Chart",
        "donut": "Donut Chart",
        "histogram": "Histogram",
        "box": "Box Plot",
        "scatter": "Scatter Plot",
        "bubble": "Bubble Chart",
        "heatmap": "Heatmap",
        "treemap": "Treemap",
        "sunburst": "Sunburst Chart",
        "choropleth": "Choropleth Map",
        "scatter_geo": "Geographic Scatter Map",
        "kpi": "KPI Cards",
    }
    return names.get(chart_type, chart_type)


# =========================================================
# FILTERS
# =========================================================
def apply_sidebar_filters(df: pd.DataFrame, chat_id: str) -> pd.DataFrame:
    filtered = df.copy()
    numeric_cols, datetime_cols, categorical_cols = detect_column_types(df)

    with st.sidebar:
        st.divider()
        st.subheader("Filters")

        filter_cols = st.multiselect(
            "Choose columns to filter",
            options=df.columns.tolist(),
            key=f"filters_{chat_id}",
        )

        for col in filter_cols:
            if col in numeric_cols:
                series = filtered[col].dropna()
                if not series.empty:
                    min_val = float(series.min())
                    max_val = float(series.max())
                    if min_val != max_val:
                        selected = st.slider(
                            col,
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            key=f"filter_num_{chat_id}_{col}",
                        )
                        filtered = filtered[(filtered[col] >= selected[0]) & (filtered[col] <= selected[1])]

            elif col in datetime_cols:
                series = filtered[col].dropna()
                if not series.empty:
                    start = series.min().date()
                    end = series.max().date()
                    selected = st.date_input(
                        col,
                        value=(start, end),
                        key=f"filter_date_{chat_id}_{col}",
                    )
                    if isinstance(selected, tuple) and len(selected) == 2:
                        filtered = filtered[
                            (filtered[col].dt.date >= selected[0]) &
                            (filtered[col].dt.date <= selected[1])
                        ]

            elif col in categorical_cols:
                values = sorted(filtered[col].dropna().astype(str).unique().tolist())
                if values and len(values) <= 100:
                    selected = st.multiselect(
                        col,
                        options=values,
                        default=values,
                        key=f"filter_cat_{chat_id}_{col}",
                    )
                    filtered = filtered[filtered[col].astype(str).isin(selected)]

    return filtered


# =========================================================
# ANALYST ENGINE / AI SUMMARY
# =========================================================
def safe_pct(part, whole) -> float:
    try:
        return (float(part) / float(whole) * 100) if whole else 0.0
    except Exception:
        return 0.0


def smart_number(value) -> str:
    if pd.isna(value):
        return "missing"
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"
        if abs(value) >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value:,.0f}"
        if value.is_integer():
            return f"{value:,.0f}"
        return f"{value:,.2f}"
    except Exception:
        return str(value)


def infer_metric_intent(col: str) -> str:
    c = col.lower()
    if any(k in c for k in ["sales", "revenue", "amount", "price", "income", "profit", "cost", "spend"]):
        return "business performance"
    if any(k in c for k in ["rating", "score", "satisfaction", "review"]):
        return "quality or customer perception"
    if any(k in c for k in ["quantity", "units", "volume", "count", "orders"]):
        return "activity volume"
    if any(k in c for k in ["age", "duration", "time", "days", "minutes"]):
        return "time or lifecycle behavior"
    return "numeric performance"


def pick_primary_metric(df: pd.DataFrame) -> Optional[str]:
    numeric_cols, _, _ = detect_column_types(df)
    priority = ["profit", "revenue", "sales", "amount", "price", "quantity", "score", "rating", "count"]
    for key in priority:
        for col in numeric_cols:
            if key in col.lower() and df[col].dropna().nunique() > 1:
                return col
    for col in numeric_cols:
        if df[col].dropna().nunique() > 1:
            return col
    return numeric_cols[0] if numeric_cols else None


def pick_primary_category(df: pd.DataFrame) -> Optional[str]:
    _, _, categorical_cols = detect_column_types(df)
    candidates = []
    for col in categorical_cols:
        n = df[col].nunique(dropna=True)
        if 2 <= n <= 30:
            name_score = 0
            cl = col.lower()
            if any(k in cl for k in ["category", "segment", "region", "type", "department", "city", "state", "country", "product", "channel"]):
                name_score += 2
            candidates.append((name_score, -n, col))
    candidates.sort(reverse=True)
    return candidates[0][2] if candidates else None


def detect_data_quality_findings(df: pd.DataFrame) -> List[str]:
    findings = []
    total_cells = max(1, df.shape[0] * df.shape[1])
    missing = int(df.isna().sum().sum())
    dupes = int(df.duplicated().sum())
    missing_pct = safe_pct(missing, total_cells)
    if missing_pct > 10:
        findings.append(f"Data completeness needs attention: {smart_number(missing)} cells are missing ({missing_pct:.1f}% of all cells), so conclusions may change after cleaning.")
    elif missing > 0:
        findings.append(f"The dataset is mostly usable, but {smart_number(missing)} blank cells should be reviewed before final decision-making.")
    else:
        findings.append("No missing values were detected, which makes the current analysis more reliable.")
    if dupes > 0:
        findings.append(f"There are {smart_number(dupes)} duplicate rows. If these are accidental repeats, totals and category counts may be inflated.")
    else:
        findings.append("No duplicate rows were detected, so record-level counts are not obviously inflated.")
    return findings


def detect_outliers(series: pd.Series) -> Dict[str, float]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {"count": 0, "pct": 0, "low": None, "high": None}
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return {"count": 0, "pct": 0, "low": q1, "high": q3}
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    count = int(((clean < low) | (clean > high)).sum())
    return {"count": count, "pct": safe_pct(count, len(clean)), "low": low, "high": high}


def build_analyst_findings(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Build a richer analyst-grade fact pack for the final AI summary.

    The LLM should not guess. This function computes the important facts first:
    executive bottom line, KPI snapshot, trends, anomalies, drivers, correlations,
    recommendations, limitations, and what-if scenarios.
    """
    numeric_cols, datetime_cols, categorical_cols = detect_column_types(df)
    primary_metric = pick_primary_metric(df)
    primary_category = pick_primary_category(df)

    findings = {
        "executive_bottom_line": [],
        "kpi_snapshot": [],
        "quality": detect_data_quality_findings(df),
        "performance": [],
        "trends": [],
        "patterns": [],
        "outliers_anomalies": [],
        "drivers": [],
        "correlations": [],
        "risks": [],
        "actions": [],
        "limitations": [],
        "what_if_scenarios": [],
    }

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = max(1, total_rows * total_cols)
    missing = int(df.isna().sum().sum())
    dupes = int(df.duplicated().sum())
    missing_pct = safe_pct(missing, total_cells)

    findings["kpi_snapshot"].append(f"Dataset size after filters: {smart_number(total_rows)} rows and {smart_number(total_cols)} columns.")
    findings["kpi_snapshot"].append(f"Data quality snapshot: {smart_number(missing)} missing cells ({missing_pct:.1f}% of all cells) and {smart_number(dupes)} duplicate rows.")

    if numeric_cols:
        usable_metrics = []
        for col in numeric_cols:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            if not s.empty and s.nunique() > 1:
                usable_metrics.append((col, s.sum(), s.mean(), s.median(), s.min(), s.max(), len(s)))
        for col, total, avg, med, mn, mx, count in usable_metrics[:5]:
            findings["kpi_snapshot"].append(
                f"{col}: total {smart_number(total)}, average {smart_number(avg)}, median {smart_number(med)}, range {smart_number(mn)} to {smart_number(mx)} across {smart_number(count)} valid records."
            )

    if primary_metric:
        s = pd.to_numeric(df[primary_metric], errors="coerce").dropna()
        if not s.empty:
            out = detect_outliers(s)
            total_metric = s.sum()
            avg_metric = s.mean()
            med_metric = s.median()
            findings["executive_bottom_line"].append(
                f"Primary metric detected: {primary_metric}. Total is {smart_number(total_metric)}, average is {smart_number(avg_metric)}, and median is {smart_number(med_metric)}."
            )
            findings["performance"].append(
                f"{primary_metric} ranges from {smart_number(s.min())} to {smart_number(s.max())}, showing the full spread of performance in the filtered dataset."
            )

            std = s.std()
            if pd.notna(std) and std > 0 and abs(avg_metric - med_metric) > std * 0.25:
                skew_side = "higher" if avg_metric > med_metric else "lower"
                findings["risks"].append(
                    f"The average {primary_metric} is noticeably {skew_side} than the median, so a few extreme records may be distorting the typical story."
                )

            if out["count"]:
                findings["outliers_anomalies"].append(
                    f"{smart_number(out['count'])} potential outliers were found in {primary_metric} ({out['pct']:.1f}% of valid values) using the IQR rule. Expected range is roughly {smart_number(out['low'])} to {smart_number(out['high'])}."
                )
            else:
                findings["outliers_anomalies"].append(
                    f"No major IQR-based outlier signal was detected in {primary_metric}."
                )

    if primary_metric and primary_category:
        temp = df[[primary_category, primary_metric]].copy()
        temp[primary_category] = _clean_label_series(temp[primary_category]) if "_clean_label_series" in globals() else temp[primary_category].fillna("Missing").astype(str)
        temp[primary_metric] = pd.to_numeric(temp[primary_metric], errors="coerce")
        grouped = temp.groupby(primary_category, dropna=False)[primary_metric].agg(["sum", "mean", "count"]).reset_index()
        grouped = grouped.sort_values("sum", ascending=False)
        if not grouped.empty:
            top = grouped.iloc[0]
            bottom = grouped.iloc[-1]
            total = grouped["sum"].sum()
            share = safe_pct(top["sum"], total)
            findings["drivers"].append(
                f"{top[primary_category]} is the strongest contributor by total {primary_metric}, contributing {smart_number(top['sum'])} ({share:.1f}% of displayed total)."
            )
            findings["drivers"].append(
                f"{bottom[primary_category]} is the weakest contributor by total {primary_metric}, contributing {smart_number(bottom['sum'])}."
            )
            findings["patterns"].append(
                f"Across {primary_category}, the top group average is {smart_number(top['mean'])} across {smart_number(top['count'])} records, while the weakest group average is {smart_number(bottom['mean'])} across {smart_number(bottom['count'])} records."
            )
            if share >= 50:
                findings["risks"].append(
                    f"Performance is concentrated: one {primary_category} group contributes more than half of total {primary_metric}. This creates dependency risk if that segment weakens."
                )
            findings["actions"].append(
                f"Compare {top[primary_category]} against {bottom[primary_category]} to identify whether the gap is caused by volume, pricing/value, customer mix, discounts, quality, or operational issues."
            )

    # Category concentration patterns even when there is no numeric metric.
    for col in categorical_cols[:5]:
        counts = _clean_label_series(df[col]).value_counts().head(10) if "_clean_label_series" in globals() else df[col].fillna("Missing").astype(str).value_counts().head(10)
        if len(counts) >= 2:
            top_name = counts.index[0]
            top_count = counts.iloc[0]
            total_count = counts.sum()
            findings["patterns"].append(
                f"In {col}, the largest visible group is {top_name} with {smart_number(top_count)} records ({safe_pct(top_count, total_count):.1f}% of the top displayed groups)."
            )

    if primary_metric and datetime_cols:
        dt = datetime_cols[0]
        trend_df = df[[dt, primary_metric]].copy().dropna(subset=[dt])
        trend_df[primary_metric] = pd.to_numeric(trend_df[primary_metric], errors="coerce")
        trend = trend_df.groupby(pd.Grouper(key=dt, freq="ME"))[primary_metric].sum().reset_index().dropna()
        trend = trend[trend[primary_metric].notna()]
        if len(trend) >= 2:
            first = trend[primary_metric].iloc[0]
            last = trend[primary_metric].iloc[-1]
            change = safe_pct(last - first, abs(first)) if first != 0 else 0
            direction = "increased" if last > first else "decreased" if last < first else "stayed flat"
            peak = trend.loc[trend[primary_metric].idxmax()]
            low = trend.loc[trend[primary_metric].idxmin()]
            findings["trends"].append(
                f"Over time, {primary_metric} {direction} from {smart_number(first)} to {smart_number(last)} ({change:+.1f}%) between the first and last monthly period."
            )
            findings["trends"].append(
                f"Peak month: {peak[dt].date()} with {smart_number(peak[primary_metric])}. Lowest month: {low[dt].date()} with {smart_number(low[primary_metric])}."
            )
            month_changes = trend[primary_metric].pct_change().replace([float("inf"), float("-inf")], pd.NA).dropna()
            if not month_changes.empty:
                biggest_jump_idx = month_changes.idxmax()
                biggest_drop_idx = month_changes.idxmin()
                findings["outliers_anomalies"].append(
                    f"Largest month-over-month jump happened around {trend.loc[biggest_jump_idx, dt].date()} ({month_changes.loc[biggest_jump_idx] * 100:+.1f}%)."
                )
                findings["outliers_anomalies"].append(
                    f"Largest month-over-month drop happened around {trend.loc[biggest_drop_idx, dt].date()} ({month_changes.loc[biggest_drop_idx] * 100:+.1f}%)."
                )
            if change < -10:
                findings["actions"].append(f"Investigate the declining periods for {primary_metric}; compare category mix, demand, discounts, missing records, or process changes before deciding strategy.")
            elif change > 10:
                findings["actions"].append(f"Identify what changed during the growth period for {primary_metric} and repeat those conditions in weaker segments.")
            findings["what_if_scenarios"].append(
                f"What if {primary_metric} improves by 5%? Estimated total would move from {smart_number(trend[primary_metric].sum())} to about {smart_number(trend[primary_metric].sum() * 1.05)} over the displayed period."
            )
            findings["what_if_scenarios"].append(
                f"What if the weakest month reaches the average monthly {primary_metric}? That would close a gap of about {smart_number(max(0, trend[primary_metric].mean() - low[primary_metric]))} for that month."
            )

    if len(numeric_cols) >= 2:
        numeric_df = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
        corr = numeric_df.corr(numeric_only=True)
        pairs = []
        for i, a in enumerate(numeric_cols):
            for b in numeric_cols[i + 1:]:
                try:
                    val = corr.loc[a, b]
                except Exception:
                    continue
                if pd.notna(val):
                    pairs.append((abs(val), val, a, b))
        pairs = sorted(pairs, reverse=True)
        for _, val, a, b in pairs[:3]:
            relationship = "move together" if val > 0 else "move in opposite directions"
            strength = "strong" if abs(val) >= 0.7 else "moderate" if abs(val) >= 0.4 else "weak"
            findings["correlations"].append(
                f"{a} and {b} {relationship} with a {strength} correlation of {val:.2f}."
            )
            if abs(val) >= 0.5:
                findings["drivers"].append(
                    f"Potential driver relationship: {a} and {b} show a correlation of {val:.2f}; validate with segmentation before assuming causation."
                )

    # Limitations and honest caveats.
    if missing > 0:
        top_missing = df.isna().sum().sort_values(ascending=False)
        top_missing = top_missing[top_missing > 0].head(3)
        if not top_missing.empty:
            missing_detail = ", ".join([f"{col}: {smart_number(cnt)}" for col, cnt in top_missing.items()])
            findings["limitations"].append(f"Missing values are concentrated in these columns: {missing_detail}. Conclusions using these fields should be treated carefully.")
    if not datetime_cols:
        findings["limitations"].append("No reliable date column was detected, so time-based growth, seasonality, and forecasting are limited.")
    if not numeric_cols:
        findings["limitations"].append("No numeric columns were detected, so KPI totals, averages, correlations, and numeric outlier checks are limited.")
    if total_rows < 30:
        findings["limitations"].append("The filtered dataset has fewer than 30 rows, so patterns may be unstable and sensitive to individual records.")

    if primary_metric:
        findings["actions"].append(f"Use {primary_metric} as the main KPI, but validate the outlier records before using averages for decisions.")
        findings["what_if_scenarios"].append(f"What if the top contributing segment drops by 10%? Estimate the impact on total {primary_metric} before committing resources to that segment.")
    if primary_category:
        findings["actions"].append(f"Create a follow-up breakdown by {primary_category} and one additional segment to understand whether performance is broad-based or concentrated.")

    if not findings["executive_bottom_line"]:
        findings["executive_bottom_line"].append(
            "The dataset is usable for exploratory analysis, but a clear business KPI could not be confidently identified from the column names and data types."
        )
    if not findings["actions"]:
        findings["actions"].append("Use the strongest categories, visible outliers, and data quality gaps as the next investigation points before making a final business decision.")
    if not findings["what_if_scenarios"]:
        findings["what_if_scenarios"].append("What if the largest category changes by ±10%? Estimate how much that would move total records or the selected KPI.")

    # Backward-compatible aliases used by the Analyst Brief cards.
    findings["performance"] = findings["executive_bottom_line"] + findings["performance"]
    findings["risks"] = findings["risks"] + findings["outliers_anomalies"][:2]

    return findings

def render_analyst_brief(df: pd.DataFrame):
    findings = build_analyst_findings(df)
    st.markdown("### Analyst Brief")
    cols = st.columns(4)
    cards = [
        ("Data Quality", findings["quality"][:2]),
        ("Performance", findings["performance"][:2]),
        ("Drivers", findings["drivers"][:2]),
        ("Recommended Actions", findings["actions"][:2]),
    ]
    for col, (title, bullets) in zip(cols, cards):
        with col:
            html = f'<div class="soft-card"><div style="font-weight:850;font-size:16px;margin-bottom:8px;">{title}</div>'
            for b in bullets:
                html += f'<div style="font-size:13px;line-height:1.45;color:#475569;margin-bottom:8px;">• {b}</div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)


def generate_ai_report_summary(df: pd.DataFrame) -> str:
    """Generate a deeper, boardroom-style AI summary from computed analyst facts."""
    numeric_cols, datetime_cols, categorical_cols = detect_column_types(df)
    findings = build_analyst_findings(df)
    compact = json.dumps(findings, indent=2, default=str)

    prompt = f"""
You are a senior business data analyst writing the final stakeholder summary for an uploaded dataset.
Use ONLY the computed findings below. Do not invent numbers, dates, column names, causes, or business facts that are not present.
Your job is to explain the "so what" clearly, like a real analyst presenting to business stakeholders.

Writing style:
- Be specific, analytical, and business-focused.
- Use plain English, but do not make it childish or too basic.
- Include concrete numbers from the computed findings whenever available.
- Separate facts from hypotheses. Use phrases like "possible explanation" or "requires investigation" when the data does not prove causation.
- Do not say vague filler like "valuable insights", "interesting patterns", or "further analysis is needed" unless you explain exactly what to analyze.
- Correlation is not causation. Never claim one metric caused another unless the findings directly prove it.

Dataset context:
- Rows after filters: {len(df)}
- Columns: {len(df.columns)}
- Numeric columns: {numeric_cols[:12]}
- Date columns: {datetime_cols[:6]}
- Category columns: {categorical_cols[:12]}

Computed analyst fact pack:
{compact}

Write the response in this exact structure:

### 1. Executive Bottom Line — The So What?
Write 4-6 sentences explaining the main business story. Mention whether the dataset appears healthy, risky, concentrated, growing/declining, or unclear based on the facts. Start with the most important KPI or pattern.

### 2. Key KPIs to Watch
Give 4-6 bullet points. Include totals, averages, medians, missing data, duplicate rows, and the main metric/category if available. Explain why each KPI matters.

### 3. Key Trends and Patterns
Give 3-5 bullet points. Discuss time movement, category concentration, top/bottom segments, seasonality-like patterns, or distribution patterns. If time data is unavailable, clearly say trend analysis is limited and explain what can still be learned from categories.

### 4. Outliers and Anomalies
Give 3-5 bullet points. Include unusual spikes/drops, IQR outliers, extreme ranges, and whether they may be real business opportunities, data errors, or cases needing investigation.

### 5. Correlations and Possible Drivers
Give 3-5 bullet points. Explain the strongest numeric relationships and the strongest category contributors. Clearly state that correlations show association, not proof of causation.

### 6. Actionable Business Recommendations
Give 4-6 concrete actions. Recommendations must be tied to findings, not generic. Use verbs like investigate, compare, reallocate, validate, segment, monitor, or forecast.

### 7. Limitations and Data Quality Notes
Give 3-5 bullet points. Mention missing values, duplicates, lack of time fields/numeric fields, small sample size, outliers, or any analysis limitation from the fact pack.

### 8. What-If Scenarios to Explore Next
Give 3 practical what-if scenarios. Examples: what if top segment drops 10%, weakest month reaches average, missing values are cleaned, budget/resources move from weak group to strong group, or primary KPI changes by 5%.

### Final Decision Note
End with 2-3 sentences telling the stakeholder what decision this analysis supports right now and what should be validated before making a final decision.
"""
    try:
        return ask_gemini(prompt)
    except Exception:
        lines = []
        lines.append("### 1. Executive Bottom Line — The So What?")
        for item in findings.get("executive_bottom_line", [])[:3]:
            lines.append(f"- {item}")
        lines.append("\n### 2. Key KPIs to Watch")
        for item in findings.get("kpi_snapshot", [])[:6]:
            lines.append(f"- {item}")
        lines.append("\n### 3. Key Trends and Patterns")
        for item in (findings.get("trends", []) + findings.get("patterns", []))[:6]:
            lines.append(f"- {item}")
        lines.append("\n### 4. Outliers and Anomalies")
        for item in findings.get("outliers_anomalies", [])[:5]:
            lines.append(f"- {item}")
        lines.append("\n### 5. Correlations and Possible Drivers")
        for item in (findings.get("correlations", []) + findings.get("drivers", []))[:6]:
            lines.append(f"- {item}")
        lines.append("\n### 6. Actionable Business Recommendations")
        for item in findings.get("actions", [])[:6]:
            lines.append(f"- {item}")
        lines.append("\n### 7. Limitations and Data Quality Notes")
        for item in (findings.get("quality", []) + findings.get("limitations", []))[:6]:
            lines.append(f"- {item}")
        lines.append("\n### 8. What-If Scenarios to Explore Next")
        for item in findings.get("what_if_scenarios", [])[:4]:
            lines.append(f"- {item}")
        lines.append("\n### Final Decision Note")
        lines.append("Use this report as a decision-support summary, not as final proof of cause and effect. Validate data quality, outliers, and the strongest segments before making a final business decision.")
        return "\n".join(lines)



# =========================================================
# PDF REPORT DOWNLOAD HELPERS
# =========================================================
def clean_markdown_for_pdf(markdown_text: str) -> str:
    """Convert simple Markdown report text into clean PDF-friendly text."""
    text = markdown_text or ""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = text.replace("—", "-").replace("–", "-").replace("•", "-")
    return text.strip()


def build_pdf_report_bytes(
    report_title: str,
    dataset_name: str,
    df: pd.DataFrame,
    summary_text: str,
) -> bytes:
    """Create a clean PDF report from the AI summary and dataset snapshot."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except Exception as e:
        raise ImportError(
            "PDF export needs the reportlab package. Add reportlab to requirements.txt and run: pip install reportlab"
        ) from e

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "LumiviseTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#172033"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "LumiviseHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#3655D4"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "LumiviseBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    story = []
    story.append(Paragraph(report_title, title_style))
    story.append(Paragraph(f"Dataset: {dataset_name or 'Uploaded dataset'}", body_style))
    story.append(Paragraph(f"Generated: {now_str()}", body_style))
    story.append(Spacer(1, 10))

    total_missing = int(df.isna().sum().sum()) if df is not None else 0
    duplicate_rows = int(df.duplicated().sum()) if df is not None else 0
    overview_data = [
        ["Rows", f"{len(df):,}"],
        ["Columns", f"{len(df.columns):,}"],
        ["Missing Values", f"{total_missing:,}"],
        ["Duplicate Rows", f"{duplicate_rows:,}"],
    ]
    overview_table = Table(overview_data, colWidths=[2.0 * inch, 4.0 * inch])
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF4FF")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#172033")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 12))

    clean_text = clean_markdown_for_pdf(summary_text)
    for raw_line in clean_text.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue
        if re.match(r"^\d+\.\s+", line) or line.lower().startswith("final decision note"):
            story.append(Paragraph(line, heading_style))
        elif line.startswith("-"):
            story.append(Paragraph(line, body_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def render_pdf_download_button(df: pd.DataFrame, summary_text: str, dataset_name: str):
    """Render a Streamlit PDF download button for the final report."""
    safe_dataset = sanitize_filename(dataset_name or "lumivise_report")
    pdf_filename = f"{os.path.splitext(safe_dataset)[0]}_Lumivise_Report.pdf"

    try:
        pdf_bytes = build_pdf_report_bytes(
            report_title="Lumivise AI Data Analyst Report",
            dataset_name=dataset_name,
            df=df,
            summary_text=summary_text,
        )
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True,
        )
    except ImportError as e:
        st.error(str(e))

# =========================================================
# UI HELPERS
# =========================================================
def render_dataset_overview(raw_df: pd.DataFrame, cleaned_filtered_df: pd.DataFrame, cleaning_report: Dict[str, int]):
    st.subheader("Dataset Quality Check")

    total_cells = max(1, raw_df.shape[0] * raw_df.shape[1])
    raw_missing = int(raw_df.isna().sum().sum())
    raw_missing_pct = safe_pct(raw_missing, total_cells)
    raw_duplicates = int(raw_df.duplicated().sum())

    render_kpi_cards([
        ("Raw Rows", f"{len(raw_df):,}", "before cleaning and filters"),
        ("Raw Columns", f"{len(raw_df.columns):,}", "before cleaning and filters"),
        ("Missing Values", f"{raw_missing:,}", f"{raw_missing_pct:.1f}% of all cells"),
        ("Duplicate Rows", f"{raw_duplicates:,}", "before cleaning"),
    ])

    if raw_missing_pct > 10:
        st.warning(
            "This dataset has high missing data. Lumivise will not blindly fill or delete missing values "
            "because some blanks may be meaningful. For best visualization results, upload a pre-cleaned dataset."
        )
    elif raw_missing > 0:
        st.info("Some missing values were found. Review column-wise missing data before making final decisions.")
    else:
        st.success("No missing values detected in the raw dataset.")

    st.markdown("### Safe Cleaning Applied")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Duplicates Removed", f"{cleaning_report['duplicates_removed']:,}")
    c2.metric("Empty Rows Removed", f"{cleaning_report['empty_rows_removed']:,}")
    c3.metric("Empty Columns Removed", f"{cleaning_report['empty_columns_removed']:,}")
    c4.metric("Missing Still Present", f"{cleaning_report['missing_values_remaining']:,}")

    st.caption(
        "Safe cleaning only: duplicate rows, fully empty rows/columns, and column-name spacing were fixed. "
        "Missing values were not blindly filled or deleted, and correct data types were not force-changed."
    )

    numeric_cols, datetime_cols, categorical_cols = detect_column_types(cleaned_filtered_df)

    st.markdown("### Cleaned Dataset Summary")
    st.write(
        f"After safe cleaning and current filters, the dataset has **{len(cleaned_filtered_df):,} rows** "
        f"and **{len(cleaned_filtered_df.columns)} columns**."
    )
    st.write(
        f"It includes **{len(numeric_cols)} numeric columns**, "
        f"**{len(categorical_cols)} categorical/text columns**, and "
        f"**{len(datetime_cols)} date columns**."
    )

    with st.expander("Column-wise Missing Values"):
        missing_df = pd.DataFrame({
            "Column": raw_df.columns,
            "Data Type": [str(raw_df[c].dtype) for c in raw_df.columns],
            "Missing Values": [int(raw_df[c].isna().sum()) for c in raw_df.columns],
            "Missing %": [round(safe_pct(raw_df[c].isna().sum(), len(raw_df)), 2) for c in raw_df.columns],
            "Unique Values": [int(raw_df[c].nunique(dropna=True)) for c in raw_df.columns],
        }).sort_values("Missing Values", ascending=False)
        st.dataframe(missing_df, use_container_width=True)


def render_analysis_header(summary: str, chart_type: str, why_used: str):
    st.markdown("### Summary")
    st.write(summary)

    st.markdown("### Visualization Used")
    st.write(f"**Chart Type:** {chart_type}")
    st.write(f"**Why this chart was used:** {why_used}")


# =========================================================
# PLAIN-ENGLISH CHART EXPLANATIONS
# =========================================================
def format_value(value) -> str:
    return smart_number(value)


def render_chart_explanation(title: str, explanation: str):
    st.markdown(
        f"""
        <div class="chart-explain">
            <b>💡 {title}</b><br>
            <span>{explanation}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def analyst_sentence_for_concentration(top_name, top_value, total, group_name, metric_name="records") -> str:
    share = safe_pct(top_value, total)
    if share >= 60:
        impact = f"This means the result is highly dependent on '{top_name}', so changes in this one group can strongly move the overall report."
    elif share >= 35:
        impact = f"This shows moderate concentration, so '{top_name}' is an important driver but not the whole story."
    else:
        impact = "The distribution is fairly spread out, so performance is not controlled by only one group."
    return f"'{top_name}' leads with {format_value(top_value)} {metric_name}, representing {share:.1f}% of the displayed total. {impact}"


def explain_category_count_chart(counts: pd.DataFrame, category_col: str, value_col: str = "Count") -> str:
    if counts.empty:
        return "This chart has no data to explain after the current filters. Try removing filters or selecting another column."
    sorted_counts = counts.sort_values(value_col, ascending=False)
    top = sorted_counts.iloc[0]
    bottom = sorted_counts.iloc[-1]
    total = sorted_counts[value_col].sum()
    share = safe_pct(top[value_col], total)
    gap = top[value_col] - bottom[value_col]
    return (
        f"This chart shows which '{category_col}' groups dominate the dataset. "
        f"{analyst_sentence_for_concentration(top[category_col], top[value_col], total, category_col, 'records')} "
        f"The gap between the largest and smallest displayed groups is {format_value(gap)} records. "
        f"Business impact: high-count groups should be prioritized for deeper analysis because they influence the overall results the most, while low-count groups may represent niche segments, weak demand, or underrepresented data."
    )


def explain_numeric_distribution(series: pd.Series, chart_name: str) -> str:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return "This chart has no numeric values to explain after the current filters."
    mean = clean.mean()
    median = clean.median()
    std = clean.std()
    out = detect_outliers(clean)
    skew_note = ""
    if mean > median * 1.15 if median != 0 else mean > median:
        skew_note = "The average is higher than the median, so a few large values are pulling the metric upward. "
    elif mean < median * 0.85 if median != 0 else mean < median:
        skew_note = "The average is lower than the median, so smaller values are pulling the metric downward. "
    else:
        skew_note = "The average and median are close, so the typical value is fairly representative. "
    out_note = f"There are {format_value(out['count'])} possible outliers ({out['pct']:.1f}%). " if out["count"] else "There are no major outlier signals using the IQR rule. "
    return (
        f"This {chart_name.lower()} explains the shape and reliability of this metric. "
        f"The median is {format_value(median)}, the average is {format_value(mean)}, and the values range from {format_value(clean.min())} to {format_value(clean.max())}. "
        f"{skew_note}{out_note}Impact: if outliers are real, they may represent high-value opportunities or problem cases; if they are data errors, they can distort decisions based on averages."
    )


def explain_scatter_chart(df: pd.DataFrame, x: str, y: str) -> str:
    temp = df[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(temp) < 3:
        return "There are not enough valid points to explain a relationship confidently."
    corr = temp.corr(numeric_only=True).iloc[0, 1]
    if corr >= 0.7:
        direction = "a strong positive relationship"
        impact = f"as {x} rises, {y} usually rises too, so {x} may be an important driver or companion metric."
    elif corr >= 0.3:
        direction = "a moderate positive relationship"
        impact = f"higher {x} is generally associated with higher {y}, but other factors also matter."
    elif corr <= -0.7:
        direction = "a strong negative relationship"
        impact = f"as {x} rises, {y} usually falls, which may reveal a trade-off or efficiency issue."
    elif corr <= -0.3:
        direction = "a moderate negative relationship"
        impact = f"higher {x} tends to come with lower {y}, but the relationship is not perfect."
    else:
        direction = "a weak or unclear relationship"
        impact = "these two fields should not be treated as strong drivers of each other without more segmentation."
    return (
        f"This chart tests whether '{x}' and '{y}' move together. The correlation is {corr:.2f}, showing {direction}. "
        f"Impact: {impact} Look for clusters or unusual points because they may reveal segments behaving differently from the overall pattern."
    )


def explain_heatmap(corr: pd.DataFrame) -> str:
    if corr.empty or corr.shape[0] < 2:
        return "There are not enough numeric columns to explain relationships."
    pairs = []
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr.loc[cols[i], cols[j]]
            if pd.notna(val):
                pairs.append((abs(val), val, cols[i], cols[j]))
    if not pairs:
        return "The heatmap did not find clear numeric relationships."
    _, val, a, b = sorted(pairs, reverse=True)[0]
    direction = "move together" if val > 0 else "move in opposite directions"
    strength = "strong" if abs(val) >= 0.7 else "moderate" if abs(val) >= 0.3 else "weak"
    return (
        f"This heatmap identifies which numeric fields are most connected. The strongest relationship is between '{a}' and '{b}' with correlation {val:.2f}, a {strength} relationship where they {direction}. "
        f"Impact: strong relationships can reveal drivers, duplication, or trade-offs. Weak relationships mean those metrics may need segmentation before drawing conclusions."
    )


def explain_trend_chart(trend: pd.DataFrame, date_col: str, value_col: str) -> str:
    if trend.empty or len(trend) < 2:
        return "This trend chart does not have enough time points to explain a meaningful movement."
    start_value = trend[value_col].iloc[0]
    end_value = trend[value_col].iloc[-1]
    peak = trend.loc[trend[value_col].idxmax()]
    low = trend.loc[trend[value_col].idxmin()]
    change = safe_pct(end_value - start_value, abs(start_value)) if start_value != 0 else 0
    direction = "increased" if end_value > start_value else "decreased" if end_value < start_value else "stayed almost the same"
    impact = "This is a positive signal if growth is desired." if change > 10 else "This needs investigation because the metric is moving downward." if change < -10 else "The metric is relatively stable, so smaller period-level changes may matter more than the overall trend."
    return (
        f"This chart shows how '{value_col}' changes over time. From the first point to the last point, it {direction} from {format_value(start_value)} to {format_value(end_value)} ({change:+.1f}%). "
        f"The highest point is {format_value(peak[value_col])} at {format_value(peak[date_col])}, while the lowest point is {format_value(low[value_col])} at {format_value(low[date_col])}. "
        f"Impact: {impact} The peak and drop periods should be compared against categories, campaigns, operations, or data quality changes."
    )


def explain_grouped_numeric_chart(grouped: pd.DataFrame, category_col: str, value_col: str, aggregation: str = "value") -> str:
    if grouped.empty:
        return "This chart has no grouped values to explain after the current filters."
    sorted_grouped = grouped.sort_values(value_col, ascending=False)
    top = sorted_grouped.iloc[0]
    bottom = sorted_grouped.iloc[-1]
    total = sorted_grouped[value_col].sum()
    share = safe_pct(top[value_col], total)
    ratio = (top[value_col] / bottom[value_col]) if bottom[value_col] not in [0, None] else None
    ratio_text = f" The top group is {ratio:.1f}x the bottom group." if ratio and ratio > 0 else ""
    return (
        f"This chart compares {aggregation} '{value_col}' across '{category_col}'. "
        f"'{top[category_col]}' leads with {format_value(top[value_col])}, contributing {share:.1f}% of the displayed total. "
        f"'{bottom[category_col]}' is lowest with {format_value(bottom[value_col])}.{ratio_text} "
        f"Impact: the leading group is likely driving the overall result, while the weakest group should be checked for low demand, poor performance, missing records, or an opportunity to improve."
    )


def explain_two_category_chart(grouped: pd.DataFrame, x: str, color: str, value_col: str = "Count") -> str:
    if grouped.empty or not color:
        return "This chart compares categories and their displayed values."
    top = grouped.sort_values(value_col, ascending=False).iloc[0]
    total = grouped[value_col].sum()
    share = safe_pct(top[value_col], total)
    return (
        f"This chart shows how '{x}' is split by '{color}'. The largest combination is '{top[x]}' + '{top[color]}' with {format_value(top[value_col])}, representing {share:.1f}% of the displayed total. "
        f"Impact: this combination is the biggest driver of the two-category pattern. If this group performs well, it can lift the whole report; if it performs poorly, it can hide weaker performance in smaller groups."
    )


def explain_hierarchy_chart(grouped: pd.DataFrame, hierarchy: List[str]) -> str:
    if grouped.empty:
        return "This hierarchy chart has no data to explain after the current filters."
    top = grouped.sort_values("value", ascending=False).iloc[0]
    total = grouped["value"].sum()
    path = " → ".join([format_value(top[h]) for h in hierarchy])
    share = safe_pct(top["value"], total)
    return (
        f"This chart breaks the data from broad groups into smaller subgroups. The largest path is {path}, with {format_value(top['value'])} ({share:.1f}% of the displayed total). "
        f"Impact: this path is the most important branch to investigate first because changes there will affect the overall outcome more than smaller branches."
    )


def explain_geo_chart(grouped: pd.DataFrame, geo_col: str, value_col: str = "value") -> str:
    if grouped.empty:
        return "This map has no geographic data to explain after the current filters."
    top = grouped.sort_values(value_col, ascending=False).iloc[0]
    total = grouped[value_col].sum()
    share = safe_pct(top[value_col], total)
    return (
        f"This map compares values by location. '{top[geo_col]}' is the highest location with {format_value(top[value_col])}, representing {share:.1f}% of the displayed total. "
        f"Impact: geographic concentration can show where demand, activity, or performance is strongest. Strong regions may deserve more investment, while weak regions may need localized investigation."
    )


# =========================================================
# REPORT SECTION RENDERERS
# =========================================================
def render_category_section(df: pd.DataFrame):
    cat_cols = choose_best_category_columns(df, max_cols=3)
    if not cat_cols:
        return

    st.header("Category Analysis")

    for idx, col in enumerate(cat_cols):
        counts = df[col].fillna("Missing").value_counts().head(10).reset_index()
        counts.columns = [col, "Count"]

        st.subheader(f"Category: {col}")
        render_analysis_header(
            summary=f"This section shows how values are distributed in **{col}**.",
            chart_type="Bar Chart and Donut Chart",
            why_used="Bar charts are best for comparing category counts. Donut charts help show category share when there are a limited number of categories.",
        )

        st.dataframe(counts, use_container_width=True, key=f"cat_table_{idx}")

        fig_bar = px.bar(counts, x=col, y="Count", title=f"Top Values in {col}")
        render_premium_chart(fig_bar, use_container_width=True, key=f"cat_bar_{idx}")
        render_chart_explanation("What this bar chart says", explain_category_count_chart(counts, col, "Count"))

        if counts.shape[0] <= 8:
            fig_donut = px.pie(counts, names=col, values="Count", hole=0.45, title=f"Share of {col}")
            render_premium_chart(fig_donut, use_container_width=True, key=f"cat_donut_{idx}")
            render_chart_explanation("What this donut chart says", explain_category_count_chart(counts, col, "Count"))

        st.divider()


def render_numeric_section(df: pd.DataFrame):
    num_cols = choose_best_numeric_columns(df, max_cols=3)
    if not num_cols:
        return

    st.header("Numeric Distribution Analysis")

    for idx, col in enumerate(num_cols):
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue

        st.subheader(f"Numeric Field: {col}")
        render_analysis_header(
            summary=f"This section shows the distribution of **{col}** without adding unnecessary charts.",
            chart_type="Histogram and Box Plot",
            why_used="Histogram shows the value distribution. Box plot shows spread and possible outliers.",
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Average", f"{series.mean():,.2f}")
        c2.metric("Median", f"{series.median():,.2f}")
        c3.metric("Max", f"{series.max():,.2f}")

        fig_hist = px.histogram(df, x=col, title=f"Distribution of {col}")
        render_premium_chart(fig_hist, use_container_width=True, key=f"num_hist_{idx}")
        render_chart_explanation("What this histogram says", explain_numeric_distribution(series, "Histogram"))

        fig_box = px.box(df, y=col, title=f"Spread and Outliers of {col}")
        render_premium_chart(fig_box, use_container_width=True, key=f"num_box_{idx}")
        render_chart_explanation("What this box plot says", explain_numeric_distribution(series, "Box Plot"))

        st.divider()

def render_relationship_section(df: pd.DataFrame):
    num_cols = choose_best_numeric_columns(df, max_cols=4)
    if len(num_cols) < 2:
        return

    st.header("Numeric Relationship Analysis")

    x = num_cols[0]
    y = num_cols[1]
    corr_value = df[[x, y]].corr(numeric_only=True).iloc[0, 1]

    render_analysis_header(
        summary=f"This section checks whether **{x}** and **{y}** move together. Their correlation is **{corr_value:.2f}**.",
        chart_type="Scatter Plot and Correlation Heatmap",
        why_used="Scatter plot shows the relationship between two numeric columns. Heatmap is only used when multiple numeric columns exist.",
    )

    fig_scatter = px.scatter(df, x=x, y=y, title=f"{x} vs {y}")
    render_premium_chart(fig_scatter, use_container_width=True, key="rel_scatter")
    render_chart_explanation("What this scatter plot says", explain_scatter_chart(df, x, y))

    if len(num_cols) >= 3:
        corr = df[num_cols].corr(numeric_only=True)
        fig_heatmap = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
        render_premium_chart(fig_heatmap, use_container_width=True, key="rel_heatmap")
        render_chart_explanation("What this heatmap says", explain_heatmap(corr))

    st.divider()

def render_trend_section(df: pd.DataFrame):
    dt_col = choose_best_datetime_column(df)
    num_cols = choose_best_numeric_columns(df, max_cols=2)

    if not dt_col or not num_cols:
        return

    st.header("Trend Analysis")

    y = num_cols[0]
    trend = df.dropna(subset=[dt_col]).groupby(dt_col, as_index=False)[y].sum()

    if trend.empty or len(trend) < 2:
        return

    render_analysis_header(
        summary=f"This section shows how **{y}** changes over **{dt_col}**.",
        chart_type="Line Chart",
        why_used="Line charts are the clearest option for showing changes over time.",
    )

    fig_line = px.line(trend, x=dt_col, y=y, title=f"Trend of {y} over {dt_col}")
    render_premium_chart(fig_line, use_container_width=True, key="trend_line")
    render_chart_explanation("What this line chart says", explain_trend_chart(trend, dt_col, y))

    st.divider()

def render_category_numeric_section(df: pd.DataFrame):
    cat_cols = choose_best_category_columns(df, max_cols=2)
    num_cols = choose_best_numeric_columns(df, max_cols=2)

    if not cat_cols or not num_cols:
        return

    st.header("Category vs Numeric Analysis")

    cat = cat_cols[0]
    num = num_cols[0]

    grouped = df.groupby(cat, dropna=False)[num].mean().reset_index()
    grouped = grouped.sort_values(num, ascending=False).head(10)

    render_analysis_header(
        summary=f"This section compares average **{num}** across **{cat}**.",
        chart_type="Bar Chart and Box Plot",
        why_used="Bar chart compares category averages. Box plot shows spread and outliers within each category.",
    )

    fig_bar = px.bar(grouped, x=cat, y=num, title=f"Average {num} by {cat}")
    render_premium_chart(fig_bar, use_container_width=True, key="cat_num_bar")
    render_chart_explanation(
        "What this bar chart says",
        explain_grouped_numeric_chart(grouped, cat, num, "average")
    )

    if df[cat].nunique(dropna=True) <= 15:
        fig_box = px.box(df, x=cat, y=num, title=f"{num} Spread by {cat}")
        render_premium_chart(fig_box, use_container_width=True, key="cat_num_box")
        render_chart_explanation(
            "What this box plot says",
            f"This box plot shows how '{num}' values vary inside each '{cat}' group. Wide spreads or far-away points mean that group has high variation or possible outliers."
        )

    st.divider()

def render_two_category_section(df: pd.DataFrame):
    cat_cols = choose_best_category_columns(df, max_cols=3)
    if len(cat_cols) < 2:
        return

    st.header("Two-Category Analysis")

    x = cat_cols[0]
    color = cat_cols[1]

    grouped = df.groupby([x, color], dropna=False).size().reset_index(name="Count")

    render_analysis_header(
        summary=f"This section compares **{x}** while splitting counts by **{color}**.",
        chart_type="Stacked Bar Chart and Heatmap",
        why_used="These charts help compare category counts and spot concentration patterns across two categorical fields.",
    )

    fig_stacked = px.bar(grouped, x=x, y="Count", color=color, title=f"{x} split by {color}")
    render_premium_chart(fig_stacked, use_container_width=True, key="two_cat_stacked")
    render_chart_explanation("What this stacked bar chart says", explain_two_category_chart(grouped, x, color, "Count"))

    pivot = grouped.pivot(index=color, columns=x, values="Count").fillna(0)
    fig_heatmap = px.imshow(pivot, text_auto=True, title=f"Heatmap of {color} vs {x}")
    render_premium_chart(fig_heatmap, use_container_width=True, key="two_cat_heatmap")
    render_chart_explanation("What this heatmap says", explain_two_category_chart(grouped, x, color, "Count"))

    st.divider()


def render_hierarchy_section(df: pd.DataFrame):
    cat_cols = choose_best_category_columns(df, max_cols=3)
    num_cols = choose_best_numeric_columns(df, max_cols=1)

    if len(cat_cols) < 2:
        return

    st.header("Hierarchy Analysis")

    hierarchy = cat_cols[:2]
    value_col = num_cols[0] if num_cols else None

    # Plotly treemap/sunburst crashes when a parent is None/NaN but child has data.
    # So we safely replace missing hierarchy labels with the text "Missing".
    temp_df = df.copy()
    for col in hierarchy:
        temp_df[col] = temp_df[col].fillna("Missing").astype(str).str.strip()
        temp_df[col] = temp_df[col].replace({"": "Missing", "nan": "Missing", "None": "Missing"})

    if value_col:
        grouped = temp_df.groupby(hierarchy, dropna=False)[value_col].sum().reset_index(name="value")
        summary = f"This section shows how **{value_col}** is distributed across the hierarchy of **{hierarchy[0]}** and **{hierarchy[1]}**."
    else:
        grouped = temp_df.groupby(hierarchy, dropna=False).size().reset_index(name="value")
        summary = f"This section shows how records are distributed across the hierarchy of **{hierarchy[0]}** and **{hierarchy[1]}**."

    grouped["value"] = pd.to_numeric(grouped["value"], errors="coerce").fillna(0)
    grouped = grouped[grouped["value"] > 0]

    if grouped.empty:
        st.info("Hierarchy chart skipped because there is not enough valid hierarchy data after cleaning missing parent labels.")
        return

    render_analysis_header(
        summary=summary,
        chart_type="Treemap and Sunburst Chart",
        why_used="These charts are useful for showing hierarchical category structure and relative size.",
    )

    fig_treemap = px.treemap(grouped, path=hierarchy, values="value", title="Treemap View")
    render_premium_chart(fig_treemap, use_container_width=True, key="hier_treemap")
    render_chart_explanation("What this treemap says", explain_hierarchy_chart(grouped, hierarchy))

    fig_sunburst = px.sunburst(grouped, path=hierarchy, values="value", title="Sunburst View")
    render_premium_chart(fig_sunburst, use_container_width=True, key="hier_sunburst")
    render_chart_explanation("What this sunburst chart says", explain_hierarchy_chart(grouped, hierarchy))

    st.divider()


COUNTRY_CODE_MAP = {
    "US": "United States",
    "IN": "India",
    "UK": "United Kingdom",
    "GB": "United Kingdom",
    "BR": "Brazil",
    "CA": "Canada",
    "DE": "Germany",
    "AU": "Australia",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "CN": "China",
    "JP": "Japan",
    "MX": "Mexico",
    "NL": "Netherlands",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SG": "Singapore",
    "ZA": "South Africa",
    "AE": "United Arab Emirates",
    "SA": "Saudi Arabia",
}

USA_STATE_CODES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC"
}


def prepare_geo_locations(series: pd.Series) -> Tuple[pd.Series, str]:
    s = series.astype(str).str.strip()
    upper = s.str.upper()

    if upper.isin(USA_STATE_CODES).mean() > 0.8:
        return upper, "USA-states"

    if upper.str.len().eq(2).mean() > 0.8:
        mapped = upper.map(COUNTRY_CODE_MAP).fillna(s)
        return mapped, "country names"

    if upper.str.len().eq(3).mean() > 0.8 and upper.str.isalpha().mean() > 0.8:
        return upper, "ISO-3"

    return s, "country names"


def render_geo_section(df: pd.DataFrame):
    geo_cols = find_geo_columns(df)
    num_cols = choose_best_numeric_columns(df, max_cols=1)

    if not any(geo_cols.values()):
        return

    st.header("Geographic Analysis")

    if geo_cols["lat"] and geo_cols["lon"]:
        render_analysis_header(
            summary="This section shows the geographic distribution of records based on latitude and longitude.",
            chart_type="Geographic Scatter Map",
            why_used="A geographic scatter map is best when exact coordinates are available.",
        )

        geo_plot_df, safe_size_col = prepare_scatter_geo_dataframe(
            df,
            geo_cols["lat"],
            geo_cols["lon"],
            num_cols[0] if num_cols else None,
        )

        if geo_plot_df.empty:
            st.info("Geographic map skipped because valid latitude/longitude rows were not found after cleaning.")
            return

        fig = px.scatter_geo(
            geo_plot_df,
            lat=geo_cols["lat"],
            lon=geo_cols["lon"],
            color=geo_cols["country"] or geo_cols["state"] or geo_cols["city"],
            size=safe_size_col,
            title="Geographic Distribution",
        )
        render_premium_chart(fig, use_container_width=True, key="geo_scatter")
        render_chart_explanation("What this geographic map says", "This map shows where records are located using latitude and longitude. Points show locations, and bigger points usually mean larger values if a size field is used.")
        st.divider()
        return

    geo_col = geo_cols["country"] or geo_cols["state"] or geo_cols["city"]
    if geo_col:
        if num_cols:
            grouped = df.groupby(geo_col, dropna=False)[num_cols[0]].sum().reset_index(name="value")
            summary = f"This map shows the distribution of **{num_cols[0]}** by **{geo_col}**."
        else:
            grouped = df.groupby(geo_col, dropna=False).size().reset_index(name="value")
            summary = f"This map shows the count of records by **{geo_col}**."

        locations, location_mode = prepare_geo_locations(grouped[geo_col])

        render_analysis_header(
            summary=summary,
            chart_type="Choropleth Map",
            why_used="A choropleth map is useful for comparing values across geographic regions.",
        )

        fig = px.choropleth(
            grouped.assign(_location=locations),
            locations="_location",
            locationmode=location_mode,
            color="value",
            hover_name=geo_col,
            title=f"Geographic View by {geo_col}",
        )
        render_premium_chart(fig, use_container_width=True, key="geo_choropleth")
        render_chart_explanation("What this choropleth map says", explain_geo_chart(grouped, geo_col, "value"))
        st.divider()


def render_final_ai_summary(df: pd.DataFrame, dataset_name: str = "Lumivise_Report"):
    st.header("Final AI Insight Summary")
    summary = generate_ai_report_summary(df)
    st.write(summary)

    st.markdown("### Export Report")
    render_pdf_download_button(df, summary, dataset_name)


# =========================================================
# VISUAL EXPLORER
# =========================================================
def render_visual_explorer(df: pd.DataFrame):
    st.subheader("🧭 Visual Explorer")

    numeric_cols, datetime_cols, categorical_cols = detect_column_types(df)
    all_cols = df.columns.tolist()
    geo_cols = find_geo_columns(df)

    chart_type = st.selectbox(
        "Chart Type",
        [
            "bar", "stacked_bar", "line", "area", "pie", "donut",
            "histogram", "box", "scatter", "bubble",
            "heatmap", "treemap", "sunburst",
            "choropleth", "scatter_geo", "kpi",
        ],
        format_func=format_chart_name,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        x = st.selectbox("X / Primary Column", options=[None] + all_cols, index=0)
    with c2:
        y = st.selectbox("Y / Measure", options=[None] + all_cols, index=0)
    with c3:
        color = st.selectbox("Color / Split", options=[None] + all_cols, index=0)
    with c4:
        size = st.selectbox("Size (for bubble/map)", options=[None] + numeric_cols, index=0)

    agg = st.selectbox("Aggregation", ["count", "sum", "mean", "median", "min", "max", "none"], index=0)
    top_n = st.slider("Top N", min_value=3, max_value=50, value=10)

    hierarchy = []
    if chart_type in {"treemap", "sunburst"}:
        hierarchy = st.multiselect("Hierarchy Columns", options=categorical_cols, default=categorical_cols[:2])

    if chart_type == "scatter_geo":
        st.caption(f"Detected geo columns: lat={geo_cols['lat']}, lon={geo_cols['lon']}, country={geo_cols['country']}, state={geo_cols['state']}, city={geo_cols['city']}")

    if st.button("Generate Visualization", use_container_width=True):
        plan = {
            "chart_type": chart_type,
            "x": x,
            "y": y,
            "color": color,
            "size": size,
            "hierarchy": hierarchy,
            "aggregation": agg,
            "top_n": top_n,
            "summary": "This visualization was generated from your manual selections.",
            "why": "The selected chart was chosen manually in the visual explorer.",
            "note": None,
        }
        render_manual_plan(df, plan)


def render_manual_plan(df: pd.DataFrame, plan: dict):
    chart_type = plan["chart_type"]
    x = plan["x"]
    y = plan["y"]
    color = plan["color"]
    size = plan["size"]
    hierarchy = plan["hierarchy"]
    aggregation = plan["aggregation"]
    summary = plan["summary"]
    why = plan["why"]

    render_analysis_header(summary, format_chart_name(chart_type), why)


    if chart_type == "kpi":
        numeric_cols = choose_best_numeric_columns(df, max_cols=3)
        if numeric_cols:
            cols = st.columns(min(3, len(numeric_cols)))
            for i, col in enumerate(numeric_cols[:3]):
                cols[i].metric(f"Average {col}", f"{df[col].dropna().mean():,.2f}")
        return

    if chart_type == "histogram" and x:
        fig = px.histogram(df, x=x, title=f"Distribution of {x}")
        render_premium_chart(fig, use_container_width=True)
        render_chart_explanation("What this histogram says", explain_numeric_distribution(df[x], "Histogram"))
        return

    if chart_type == "box" and y:
        fig = px.box(df, x=x if x else None, y=y, color=color if color else None, title=f"{y} by {x}" if x else f"Box Plot of {y}")
        render_premium_chart(fig, use_container_width=True)
        render_chart_explanation("What this box plot says", explain_numeric_distribution(df[y], "Box Plot"))
        return


    if chart_type == "scatter" and x and y:
        fig = px.scatter(df, x=x, y=y, color=color if color else None, title=f"{x} vs {y}")
        render_premium_chart(fig, use_container_width=True)
        render_chart_explanation("What this scatter plot says", explain_scatter_chart(df, x, y))
        return

    if chart_type == "bubble" and x and y:
        fig = px.scatter(df, x=x, y=y, size=size if size else None, color=color if color else None, title=f"{x} vs {y}")
        render_premium_chart(fig, use_container_width=True)
        render_chart_explanation("What this bubble chart says", explain_scatter_chart(df, x, y))
        return

    if chart_type == "heatmap":
        numeric_cols, _, _ = detect_column_types(df)
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this heatmap says", explain_heatmap(corr))
        return

    if chart_type in {"treemap", "sunburst"} and hierarchy:
        # IMPORTANT FIX: Plotly hierarchy charts cannot handle None/NaN parent labels.
        # Convert missing parent/child labels into "Missing" before grouping.
        temp_df = df.copy()
        for col in hierarchy:
            temp_df[col] = temp_df[col].fillna("Missing").astype(str).str.strip()
            temp_df[col] = temp_df[col].replace({"": "Missing", "nan": "Missing", "None": "Missing"})

        if y and aggregation != "count":
            grouped = temp_df.groupby(hierarchy, dropna=False)[y].sum().reset_index(name="value")
        else:
            grouped = temp_df.groupby(hierarchy, dropna=False).size().reset_index(name="value")

        grouped["value"] = pd.to_numeric(grouped["value"], errors="coerce").fillna(0)
        grouped = grouped[grouped["value"] > 0]

        if grouped.empty:
            st.info("This hierarchy chart was skipped because there is not enough valid data after handling missing labels.")
            return

        if chart_type == "treemap":
            fig = px.treemap(grouped, path=hierarchy, values="value", title="Treemap View")
        else:
            fig = px.sunburst(grouped, path=hierarchy, values="value", title="Sunburst View")
        render_premium_chart(fig, use_container_width=True)
        render_chart_explanation(f"What this {format_chart_name(chart_type).lower()} says", explain_hierarchy_chart(grouped, hierarchy))
        return

    if chart_type == "scatter_geo":
        geo_cols = find_geo_columns(df)
        lat = geo_cols["lat"]
        lon = geo_cols["lon"]
        if lat and lon:
            fig = px.scatter_geo(df, lat=lat, lon=lon, color=color if color else None, size=size if size else None, title="Geographic Distribution")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this geographic map says", "This map shows where records are located using latitude and longitude. Points show locations, and bigger points usually mean larger values if a size field is used.")
        return

    if chart_type == "choropleth":
        geo_col = x if x else (find_geo_columns(df)["country"] or find_geo_columns(df)["state"] or find_geo_columns(df)["city"])
        if geo_col:
            grouped = df.groupby(geo_col, dropna=False)[y].sum().reset_index(name="value") if y and aggregation != "count" else df.groupby(geo_col, dropna=False).size().reset_index(name="value")
            locations, location_mode = prepare_geo_locations(grouped[geo_col])
            fig = px.choropleth(grouped.assign(_location=locations), locations="_location", locationmode=location_mode, color="value", hover_name=geo_col, title=f"Geographic View by {geo_col}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this choropleth map says", explain_geo_chart(grouped, geo_col, "value"))
        return

    # Aggregated charts
    if x:
        group_cols = [x]
        if chart_type == "stacked_bar" and color:
            group_cols = [x, color]

        if y and aggregation != "count":
            grouped = df.groupby(group_cols, dropna=False)[y]
            if aggregation == "sum":
                grouped = grouped.sum().reset_index(name="value")
            elif aggregation == "mean":
                grouped = grouped.mean().reset_index(name="value")
            elif aggregation == "median":
                grouped = grouped.median().reset_index(name="value")
            elif aggregation == "min":
                grouped = grouped.min().reset_index(name="value")
            elif aggregation == "max":
                grouped = grouped.max().reset_index(name="value")
            else:
                grouped = grouped.sum().reset_index(name="value")
        else:
            grouped = df.groupby(group_cols, dropna=False).size().reset_index(name="value")

        if len(group_cols) == 1:
            grouped = grouped.sort_values("value", ascending=False).head(plan["top_n"])

        if chart_type == "bar":
            fig = px.bar(grouped, x=x, y="value", color=color if color in grouped.columns else None, title=f"{aggregation.title()} by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this bar chart says", explain_grouped_numeric_chart(grouped, x, "value", aggregation))
            return

        if chart_type == "stacked_bar":
            fig = px.bar(grouped, x=x, y="value", color=color if color else None, title=f"{aggregation.title()} by {x}")
            render_premium_chart(fig, use_container_width=True)
            explanation = explain_two_category_chart(grouped.rename(columns={"value": "Count"}), x, color, "Count") if color and color in grouped.columns else explain_grouped_numeric_chart(grouped, x, "value", aggregation)
            render_chart_explanation("What this stacked bar chart says", explanation)
            return

        if chart_type == "pie":
            fig = px.pie(grouped, names=x, values="value", title=f"{aggregation.title()} share by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this pie chart says", explain_grouped_numeric_chart(grouped, x, "value", aggregation))
            return

        if chart_type == "donut":
            fig = px.pie(grouped, names=x, values="value", hole=0.45, title=f"{aggregation.title()} share by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this donut chart says", explain_grouped_numeric_chart(grouped, x, "value", aggregation))
            return

        if chart_type == "line":
            grouped = grouped.sort_values(x)
            fig = px.line(grouped, x=x, y="value", color=color if color in grouped.columns else None, title=f"{aggregation.title()} by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this line chart says", explain_trend_chart(grouped, x, "value"))
            return

        if chart_type == "area":
            grouped = grouped.sort_values(x)
            fig = px.area(grouped, x=x, y="value", color=color if color in grouped.columns else None, title=f"{aggregation.title()} by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this area chart says", explain_trend_chart(grouped, x, "value"))
            return




# =========================================================
# POWER BI-STYLE VISUAL ANALYSER
# =========================================================
def _clean_label_series(series: pd.Series) -> pd.Series:
    """Make category labels safe for charts without changing the real dataframe."""
    return (
        series.fillna("Missing")
        .astype(str)
        .str.strip()
        .replace({"": "Missing", "nan": "Missing", "None": "Missing", "NaN": "Missing"})
    )


def _aggregate_for_visual(
    df: pd.DataFrame,
    group_cols: List[str],
    measure_col: Optional[str],
    aggregation: str,
    top_n: int,
    sort_order: str,
) -> pd.DataFrame:
    """Create a Power BI-like summarized table for most visuals."""
    temp_df = df.copy()

    for col in group_cols:
        if col and col in temp_df.columns:
            temp_df[col] = _clean_label_series(temp_df[col])

    valid_group_cols = [c for c in group_cols if c and c in temp_df.columns]

    if measure_col and measure_col in temp_df.columns and aggregation != "count":
        temp_df[measure_col] = pd.to_numeric(temp_df[measure_col], errors="coerce")
        grouped_obj = temp_df.groupby(valid_group_cols, dropna=False)[measure_col] if valid_group_cols else temp_df[measure_col]

        if valid_group_cols:
            if aggregation == "sum":
                grouped = grouped_obj.sum().reset_index(name="value")
            elif aggregation == "mean":
                grouped = grouped_obj.mean().reset_index(name="value")
            elif aggregation == "median":
                grouped = grouped_obj.median().reset_index(name="value")
            elif aggregation == "min":
                grouped = grouped_obj.min().reset_index(name="value")
            elif aggregation == "max":
                grouped = grouped_obj.max().reset_index(name="value")
            else:
                grouped = grouped_obj.sum().reset_index(name="value")
        else:
            grouped = pd.DataFrame({"Metric": [measure_col], "value": [getattr(grouped_obj, aggregation)() if hasattr(grouped_obj, aggregation) else grouped_obj.sum()]})
    else:
        if valid_group_cols:
            grouped = temp_df.groupby(valid_group_cols, dropna=False).size().reset_index(name="value")
        else:
            grouped = pd.DataFrame({"Metric": ["Records"], "value": [len(temp_df)]})

    grouped["value"] = pd.to_numeric(grouped["value"], errors="coerce").fillna(0)

    ascending = sort_order == "Ascending"
    if len(valid_group_cols) <= 1 and "value" in grouped.columns:
        grouped = grouped.sort_values("value", ascending=ascending).head(top_n)
    elif "value" in grouped.columns:
        grouped = grouped.sort_values("value", ascending=ascending)

    return grouped


def _visual_insight(grouped: pd.DataFrame, x: Optional[str], y_label: str = "value") -> str:
    if grouped is None or grouped.empty or "value" not in grouped.columns:
        return "This visual does not have enough data to generate an insight. Try changing fields or removing filters."

    top = grouped.sort_values("value", ascending=False).iloc[0]
    total = grouped["value"].sum()
    share = safe_pct(top["value"], total)

    if x and x in grouped.columns:
        top_name = top[x]
        return (
            f"The strongest visible driver is '{top_name}' with {smart_number(top['value'])}, "
            f"representing {share:.1f}% of the displayed total. "
            f"Use this as the first segment to investigate, then compare it against lower-performing segments."
        )

    return f"The displayed total is {smart_number(total)} across the selected records."


def _render_powerbi_kpis(df: pd.DataFrame, measure_cols: List[str]):
    st.markdown("### Dashboard KPIs")
    total_rows = len(df)
    total_missing = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    kpis = [
        ("Records", f"{total_rows:,}", "after filters"),
        ("Columns", f"{len(df.columns):,}", "available fields"),
        ("Missing", f"{total_missing:,}", "remaining blanks"),
        ("Duplicates", f"{duplicate_rows:,}", "after cleaning/filtering"),
    ]

    if measure_cols:
        first_measure = measure_cols[0]
        s = pd.to_numeric(df[first_measure], errors="coerce").dropna()
        if not s.empty:
            kpis[2] = (f"Avg {shorten(first_measure, 16)}", smart_number(s.mean()), "selected measure")
            kpis[3] = (f"Total {shorten(first_measure, 16)}", smart_number(s.sum()), "selected measure")

    render_kpi_cards(kpis)


def _recommended_visuals(df: pd.DataFrame) -> List[str]:
    numeric_cols, datetime_cols, categorical_cols = detect_column_types(df)
    recs = []
    if categorical_cols:
        recs.append("Bar Chart: compare categories by count or measure")
    if datetime_cols and numeric_cols:
        recs.append("Line Chart: analyze trend over time")
    if len(numeric_cols) >= 2:
        recs.append("Scatter Plot: compare relationships between two numeric fields")
        recs.append("Heatmap: check numeric correlations")
    if len(categorical_cols) >= 2:
        recs.append("Treemap: explore hierarchy and contribution")
    if find_geo_columns(df).get("lat") and find_geo_columns(df).get("lon"):
        recs.append("Map: analyze geographic spread")
    return recs or ["Upload a dataset with numeric, categorical, or date fields to unlock more visual options."]


def render_visual_explorer(df: pd.DataFrame):
    """Power BI-like interactive analyser for users who want to play with data manually."""
    st.subheader("🧭 Visual Analyser")
    st.caption(
        "Use this like a mini Power BI canvas: choose fields, measures, slicers, sorting, Top N, and visualization type. "
        "This uses the safely cleaned + currently filtered dataset."
    )

    if df.empty:
        st.warning("No rows available after filters. Remove some filters to build visuals.")
        return

    numeric_cols, datetime_cols, categorical_cols = detect_column_types(df)
    all_cols = df.columns.tolist()
    geo_cols = find_geo_columns(df)

    if "powerbi_saved_visuals" not in st.session_state:
        st.session_state.powerbi_saved_visuals = []

    _render_powerbi_kpis(df, numeric_cols[:1])

    with st.expander("Recommended visuals for this dataset", expanded=False):
        for rec in _recommended_visuals(df):
            st.write(f"• {rec}")

    left, canvas = st.columns([1.05, 2.3], gap="large")

    with left:
        st.markdown("### Fields & Build Visual")

        chart_type = st.selectbox(
            "Visualization",
            [
                "bar", "stacked_bar", "line", "area", "pie", "donut",
                "histogram", "box", "scatter", "bubble",
                "heatmap", "treemap", "sunburst",
                "choropleth", "scatter_geo", "kpi",
            ],
            format_func=format_chart_name,
            key="pbi_chart_type",
        )

        x_options = [None] + all_cols
        y_options = [None] + numeric_cols
        color_options = [None] + categorical_cols + numeric_cols

        x = st.selectbox("Axis / Category / Date", options=x_options, index=0, key="pbi_x")
        y = st.selectbox("Values / Measure", options=y_options, index=0, key="pbi_y")
        color = st.selectbox("Legend / Split / Color", options=color_options, index=0, key="pbi_color")
        size = st.selectbox("Size", options=[None] + numeric_cols, index=0, key="pbi_size")

        aggregation = st.selectbox(
            "Aggregation",
            ["count", "sum", "mean", "median", "min", "max"],
            index=0,
            key="pbi_agg",
            help="Use count when you want record counts. Use sum/mean/etc. when a numeric measure is selected.",
        )

        top_n = st.slider("Top N", min_value=3, max_value=100, value=10, key="pbi_top_n")
        sort_order = st.radio("Sort", ["Descending", "Ascending"], horizontal=True, key="pbi_sort")

        hierarchy = []
        if chart_type in {"treemap", "sunburst"}:
            hierarchy = st.multiselect(
                "Hierarchy fields",
                options=categorical_cols,
                default=categorical_cols[:2],
                key="pbi_hierarchy",
                help="Choose parent to child fields. Missing labels will be shown as 'Missing' instead of crashing the chart.",
            )

        st.markdown("### Slicers")
        slicer_cols = st.multiselect(
            "Add slicers",
            options=all_cols,
            default=[],
            key="pbi_slicer_cols",
        )

        analyser_df = df.copy()
        for slicer_col in slicer_cols:
            if slicer_col in numeric_cols:
                s = pd.to_numeric(analyser_df[slicer_col], errors="coerce").dropna()
                if not s.empty and s.min() != s.max():
                    selected_range = st.slider(
                        f"{slicer_col}",
                        float(s.min()),
                        float(s.max()),
                        (float(s.min()), float(s.max())),
                        key=f"pbi_slicer_num_{slicer_col}",
                    )
                    analyser_df = analyser_df[
                        (pd.to_numeric(analyser_df[slicer_col], errors="coerce") >= selected_range[0]) &
                        (pd.to_numeric(analyser_df[slicer_col], errors="coerce") <= selected_range[1])
                    ]
            elif slicer_col in datetime_cols:
                s = analyser_df[slicer_col].dropna()
                if not s.empty:
                    selected_dates = st.date_input(
                        f"{slicer_col}",
                        value=(s.min().date(), s.max().date()),
                        key=f"pbi_slicer_date_{slicer_col}",
                    )
                    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                        analyser_df = analyser_df[
                            (analyser_df[slicer_col].dt.date >= selected_dates[0]) &
                            (analyser_df[slicer_col].dt.date <= selected_dates[1])
                        ]
            else:
                values = sorted(_clean_label_series(analyser_df[slicer_col]).unique().tolist())
                if values:
                    default_values = values[: min(len(values), 25)] if len(values) > 25 else values
                    selected_values = st.multiselect(
                        f"{slicer_col}",
                        options=values,
                        default=default_values,
                        key=f"pbi_slicer_cat_{slicer_col}",
                    )
                    analyser_df = analyser_df[_clean_label_series(analyser_df[slicer_col]).isin(selected_values)]

        st.info(f"Rows available on canvas: {len(analyser_df):,}")

        build_col, save_col = st.columns(2)
        build_clicked = build_col.button("Generate", use_container_width=True, key="pbi_generate")
        save_clicked = save_col.button("Add to Canvas", use_container_width=True, key="pbi_add_canvas")

    plan = {
        "chart_type": chart_type,
        "x": x,
        "y": y,
        "color": color,
        "size": size,
        "hierarchy": hierarchy,
        "aggregation": aggregation,
        "top_n": top_n,
        "sort_order": sort_order,
        "summary": "This visual was created from your manual field selections, similar to building a Power BI visual.",
        "why": "The analyser lets you choose fields, measures, aggregation, sorting, slicers, and chart type instead of relying on the auto report.",
        "note": None,
    }

    if save_clicked:
        st.session_state.powerbi_saved_visuals.append(plan.copy())
        st.success("Visual added to dashboard canvas.")

    with canvas:
        st.markdown("### Report Canvas")
        c1, c2, c3 = st.columns(3)
        c1.metric("Canvas Rows", f"{len(analyser_df):,}")
        c2.metric("Numeric Fields", f"{len(numeric_cols):,}")
        c3.metric("Category Fields", f"{len(categorical_cols):,}")

        render_manual_plan(analyser_df, plan)

        st.divider()
        st.markdown("### Saved Visual Canvas")
        if st.session_state.powerbi_saved_visuals:
            clear_col, count_col = st.columns([1, 3])
            if clear_col.button("Clear Canvas", use_container_width=True, key="pbi_clear_canvas"):
                st.session_state.powerbi_saved_visuals = []
                st.rerun()
            count_col.caption(f"{len(st.session_state.powerbi_saved_visuals)} visual(s) saved in this session.")

            for idx, saved_plan in enumerate(st.session_state.powerbi_saved_visuals, start=1):
                with st.expander(f"Visual {idx}: {format_chart_name(saved_plan['chart_type'])}", expanded=False):
                    render_manual_plan(analyser_df, saved_plan)
        else:
            st.info("Click 'Add to Canvas' to save visuals here while you explore the data.")


def render_manual_plan(df: pd.DataFrame, plan: dict):
    chart_type = plan.get("chart_type")
    x = plan.get("x")
    y = plan.get("y")
    color = plan.get("color")
    size = plan.get("size")
    hierarchy = plan.get("hierarchy") or []
    aggregation = plan.get("aggregation", "count")
    top_n = int(plan.get("top_n", 10))
    sort_order = plan.get("sort_order", "Descending")
    summary = plan.get("summary", "Manual visual")
    why = plan.get("why", "User-selected visual")

    render_analysis_header(summary, format_chart_name(chart_type), why)

    if df.empty:
        st.warning("No data available for this visual after slicers/filters.")
        return

    numeric_cols, datetime_cols, categorical_cols = detect_column_types(df)

    try:
        if chart_type == "kpi":
            if y and y in numeric_cols:
                s = pd.to_numeric(df[y], errors="coerce").dropna()
                render_kpi_cards([
                    ("Total", smart_number(s.sum()), y),
                    ("Average", smart_number(s.mean()), y),
                    ("Median", smart_number(s.median()), y),
                    ("Records", f"{len(df):,}", "filtered rows"),
                ])
            else:
                render_kpi_cards([
                    ("Records", f"{len(df):,}", "filtered rows"),
                    ("Columns", f"{len(df.columns):,}", "available fields"),
                    ("Missing", f"{int(df.isna().sum().sum()):,}", "blank cells"),
                    ("Duplicates", f"{int(df.duplicated().sum()):,}", "duplicate rows"),
                ])
            return

        if chart_type == "histogram":
            if not x:
                st.info("Select a numeric column in Axis / Category / Date for a histogram.")
                return
            fig = px.histogram(df, x=x, color=color if color else None, title=f"Distribution of {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this histogram says", explain_numeric_distribution(df[x], "Histogram"))
            return

        if chart_type == "box":
            if not y:
                st.info("Select a numeric measure for a box plot.")
                return
            fig = px.box(df, x=x if x else None, y=y, color=color if color else None, title=f"{y} by {x}" if x else f"Box Plot of {y}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this box plot says", explain_numeric_distribution(df[y], "Box Plot"))
            return

        if chart_type in {"scatter", "bubble"}:
            if not x or not y:
                st.info("Select both X and Y fields for this chart.")
                return
            fig = px.scatter(
                df,
                x=x,
                y=y,
                color=color if color else None,
                size=size if chart_type == "bubble" and size else None,
                title=f"{x} vs {y}",
            )
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation(f"What this {format_chart_name(chart_type).lower()} says", explain_scatter_chart(df, x, y))
            return

        if chart_type == "heatmap":
            if len(numeric_cols) < 2:
                st.info("Heatmap needs at least two numeric columns.")
                return
            corr = df[numeric_cols].corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this heatmap says", explain_heatmap(corr))
            return

        if chart_type in {"treemap", "sunburst"}:
            if len(hierarchy) < 1:
                st.info("Select at least one hierarchy field.")
                return
            measure = y if y in numeric_cols else None
            grouped = _aggregate_for_visual(df, hierarchy, measure, aggregation, top_n, sort_order)
            grouped = grouped[grouped["value"] > 0]
            if grouped.empty:
                st.info("Not enough valid hierarchy data to draw this visual.")
                return
            if chart_type == "treemap":
                fig = px.treemap(grouped, path=hierarchy, values="value", color="value", title="Treemap View")
            else:
                fig = px.sunburst(grouped, path=hierarchy, values="value", color="value", title="Sunburst View")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation(f"What this {format_chart_name(chart_type).lower()} says", explain_hierarchy_chart(grouped, hierarchy))
            return

        if chart_type == "scatter_geo":
            geo_cols = find_geo_columns(df)
            lat = geo_cols["lat"]
            lon = geo_cols["lon"]
            if not lat or not lon:
                st.info("Map needs latitude and longitude columns. They were not detected in this dataset.")
                return
            geo_plot_df, safe_size_col = prepare_scatter_geo_dataframe(df, lat, lon, size if size else None)
            if geo_plot_df.empty:
                st.info("Map could not be drawn because valid latitude/longitude rows were not found after cleaning.")
                return
            fig = px.scatter_geo(
                geo_plot_df,
                lat=lat,
                lon=lon,
                color=color if color else None,
                size=safe_size_col,
                title="Geographic Distribution",
            )
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this geographic map says", "This map shows where records are located using latitude and longitude. Use slicers and color fields to compare location patterns like Power BI map visuals.")
            return

        if chart_type == "choropleth":
            geo_col = x if x else (find_geo_columns(df)["country"] or find_geo_columns(df)["state"] or find_geo_columns(df)["city"])
            if not geo_col:
                st.info("Choose a country/state/city column for choropleth mapping.")
                return
            measure = y if y in numeric_cols else None
            grouped = _aggregate_for_visual(df, [geo_col], measure, aggregation, top_n, sort_order)
            locations, location_mode = prepare_geo_locations(grouped[geo_col])
            fig = px.choropleth(
                grouped.assign(_location=locations),
                locations="_location",
                locationmode=location_mode,
                color="value",
                hover_name=geo_col,
                title=f"Geographic View by {geo_col}",
            )
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this choropleth map says", explain_geo_chart(grouped, geo_col, "value"))
            return

        if not x:
            st.info("Select an Axis / Category / Date field to generate this visual.")
            return

        group_cols = [x]
        if chart_type == "stacked_bar" and color:
            group_cols = [x, color]

        measure = y if y in numeric_cols else None
        grouped = _aggregate_for_visual(df, group_cols, measure, aggregation, top_n, sort_order)

        color_for_fig = color if color and color in grouped.columns else None
        title_measure = aggregation.title() if aggregation == "count" else f"{aggregation.title()} of {y}"

        if chart_type == "bar":
            fig = px.bar(grouped, x=x, y="value", color=color_for_fig, title=f"{title_measure} by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this bar chart says", _visual_insight(grouped, x))
            return

        if chart_type == "stacked_bar":
            fig = px.bar(grouped, x=x, y="value", color=color_for_fig, title=f"{title_measure} by {x}")
            render_premium_chart(fig, use_container_width=True)
            explanation = explain_two_category_chart(grouped.rename(columns={"value": "Count"}), x, color, "Count") if color_for_fig else _visual_insight(grouped, x)
            render_chart_explanation("What this stacked bar chart says", explanation)
            return

        if chart_type == "pie":
            fig = px.pie(grouped, names=x, values="value", title=f"{title_measure} Share by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this pie chart says", _visual_insight(grouped, x))
            return

        if chart_type == "donut":
            fig = px.pie(grouped, names=x, values="value", hole=0.45, title=f"{title_measure} Share by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this donut chart says", _visual_insight(grouped, x))
            return

        if chart_type == "line":
            grouped = grouped.sort_values(x)
            fig = px.line(grouped, x=x, y="value", color=color_for_fig, markers=True, title=f"{title_measure} by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this line chart says", explain_trend_chart(grouped, x, "value") if len(grouped) >= 2 else _visual_insight(grouped, x))
            return

        if chart_type == "area":
            grouped = grouped.sort_values(x)
            fig = px.area(grouped, x=x, y="value", color=color_for_fig, title=f"{title_measure} by {x}")
            render_premium_chart(fig, use_container_width=True)
            render_chart_explanation("What this area chart says", explain_trend_chart(grouped, x, "value") if len(grouped) >= 2 else _visual_insight(grouped, x))
            return

        st.info("Choose fields that match the selected visual type.")

    except Exception as e:
        st.error(f"Visual could not be generated: {e}")
        st.caption("Try a different field combination, remove high-cardinality text columns, or use a pre-cleaned dataset for better visuals.")

# =========================================================
# SESSION STATE
# =========================================================
if "current_chat_id" not in st.session_state:
    existing = load_all_chats()
    if existing:
        st.session_state.current_chat_id = existing[0]["chat_id"]
    else:
        st.session_state.current_chat_id = create_new_chat()["chat_id"]

if "dataset_ready" not in st.session_state:
    st.session_state.dataset_ready = False

if "last_uploaded_chat_id" not in st.session_state:
    st.session_state.last_uploaded_chat_id = None

if "last_uploaded_file_name" not in st.session_state:
    st.session_state.last_uploaded_file_name = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("### Chat History")

    if st.button("➕ New Report", use_container_width=True, key="new_report_btn"):
        st.session_state.current_chat_id = create_new_chat("New Report")["chat_id"]
        st.rerun()

    chats = load_all_chats()

    if chats:
        for chat_item in chats:
            chat_id = chat_item["chat_id"]
            title = chat_item.get("title") or chat_item.get("dataset_name") or "No Dataset"
            is_selected = chat_id == st.session_state.current_chat_id

            chat_col, menu_col = st.columns([5, 1])

            with chat_col:
                label = f"{'' if is_selected else '📄 '}{shorten(title, 30)}"
                if st.button(label, key=f"chat_select_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()

            with menu_col:
                if st.button("⋮", key=f"menu_btn_{chat_id}", help="Rename or delete report"):
                    st.session_state[f"show_menu_{chat_id}"] = not st.session_state.get(f"show_menu_{chat_id}", False)

            if st.session_state.get(f"show_menu_{chat_id}", False):
                with st.container():
                    new_title = st.text_input(
                        "Rename report",
                        value=title,
                        key=f"rename_input_{chat_id}",
                        label_visibility="collapsed",
                    )

                    action_col1, action_col2 = st.columns(2)

                    with action_col1:
                        if st.button("Save", key=f"rename_save_{chat_id}", use_container_width=True):
                            rename_chat(chat_id, new_title)
                            st.session_state[f"show_menu_{chat_id}"] = False
                            st.rerun()

                    with action_col2:
                        if st.button("Delete", key=f"delete_report_{chat_id}", use_container_width=True):
                            delete_chat(chat_id)
                            remaining = load_all_chats()
                            if remaining:
                                st.session_state.current_chat_id = remaining[0]["chat_id"]
                            else:
                                st.session_state.current_chat_id = create_new_chat("New Report")["chat_id"]
                            st.rerun()

            st.divider()

    st.caption("Each report keeps its own dataset and filters.")



def render_sidebar_report_info(chat: dict):
    """Render Report Info in the sidebar. Call this after filters so filters stay above it."""
    with st.sidebar:
        st.divider()
        st.markdown(f"""
        <div class="sidebar-report-card">
            <div class="sidebar-report-head">
                <div class="sidebar-report-icon">📊</div>
                <div>
                    <div class="sidebar-report-title">Report Info</div>
                    <div class="sidebar-report-subtitle">Current workspace</div>
                </div>
            </div>
            <div class="sidebar-info-row">
                <div class="sidebar-info-label">Title</div>
                <div class="sidebar-info-value">{chat.get('title') or 'New Report'}</div>
            </div>
            <div class="sidebar-info-row">
                <div class="sidebar-info-label">Created</div>
                <div class="sidebar-info-value">{chat.get('created_at', '-')}</div>
            </div>
            <div class="sidebar-info-row">
                <div class="sidebar-info-label">Updated</div>
                <div class="sidebar-info-value">{chat.get('updated_at', '-')}</div>
            </div>
            <div class="sidebar-info-row">
                <div class="sidebar-info-label">Dataset</div>
                <div class="sidebar-info-value">{chat.get('dataset_name') or 'No dataset uploaded'}</div>
            </div>
            <div class="sidebar-info-row">
                <div class="sidebar-info-label">Model</div>
                <div class="sidebar-info-value">{MODEL_NAME}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# MAIN
# =========================================================
chat = load_chat(st.session_state.current_chat_id)

uploader_key = f"uploader_{chat['chat_id']}_{chat.get('updated_at', '')}"
uploaded_file = st.file_uploader(
    "Upload dataset for this report",
    type=["csv", "xlsx"],
    key=uploader_key,
)

if uploaded_file is not None:
    chat = update_chat_dataset(chat, uploaded_file)
    st.session_state.last_uploaded_chat_id = chat["chat_id"]
    st.session_state.last_uploaded_file_name = uploaded_file.name
    st.session_state.dataset_ready = True
    st.rerun()

# =========================================================
# LOAD DATA
# =========================================================
chat = load_chat(st.session_state.current_chat_id)

raw_df = None
cleaned_df = None
cleaning_report = None

if chat.get("dataset_path"):
    try:
        raw_df = load_dataframe_from_path(chat["dataset_path"])

        # Safe cleaning first. This does not blindly fill missing values or force-change data types.
        cleaned_df, cleaning_report = basic_safe_cleaning(raw_df)

        # Convert only columns that strongly look like dates, after safe cleaning.
        cleaned_df = try_convert_datetime_columns(cleaned_df)

        if st.session_state.dataset_ready and st.session_state.last_uploaded_chat_id == chat["chat_id"]:
            st.success(f"Dataset loaded successfully: {st.session_state.last_uploaded_file_name}")
            st.session_state.dataset_ready = False
    except Exception as e:
        st.error(f"Dataset loading error: {e}")

if raw_df is None or cleaned_df is None:
    st.info("Upload a CSV or XLSX file to generate the report.")
    st.stop()

filtered_df = apply_sidebar_filters(cleaned_df, chat["chat_id"])

# Report Info is intentionally rendered AFTER filters so the sidebar order is:
# Chat History -> Rename/Delete -> Filters -> Report Info
render_sidebar_report_info(chat)

tabs = st.tabs(["Auto Report", "Visual Explorer"])

# =========================================================
# AUTO REPORT TAB
# =========================================================
with tabs[0]:

    render_dataset_overview(raw_df, filtered_df, cleaning_report)
    render_analyst_brief(filtered_df)

    st.divider()
    render_category_section(filtered_df)
    render_numeric_section(filtered_df)
    render_relationship_section(filtered_df)
    render_trend_section(filtered_df)
    render_category_numeric_section(filtered_df)
    render_two_category_section(filtered_df)
    render_hierarchy_section(filtered_df)
    render_geo_section(filtered_df)
    render_final_ai_summary(filtered_df, chat.get("dataset_name", "Lumivise_Report"))

# =========================================================
# VISUAL EXPLORER TAB
# =========================================================
with tabs[1]:
    st.caption("Visual Explorer uses the safely cleaned + currently filtered dataset. It does not generate a raw data table page.")
    render_visual_explorer(filtered_df)
