# 🚀 Lumivise – AI Data Analyst Dashboard

**Illuminate. Visualize. Summarize.**

Lumivise is a **premium AI-powered Business Intelligence (BI) dashboard generator** that transforms raw datasets into **interactive visualizations, analyst-grade insights, and executive-level summaries** — all in one place.

It acts like a **Personal AI Data Analyst**:

> Upload data → Clean → Visualize → Explain → Summarize → Download report 📄

---

## ✨ Features

### 📊 1. Smart Data Processing
- Safe, non-destructive cleaning  
- Removes:
  - Duplicate rows  
  - Empty rows & columns  
- Preserves:
  - Original data types  
  - Missing values (no blind filling)

---

### 📈 2. Automated Visualization Engine
Automatically detects:
- Numeric columns  
- Categorical columns  
- Date/time columns  

Generates only **relevant charts** (no unnecessary visuals):
- Bar Charts  
- Line Charts  
- Scatter Plots  
- Histograms  
- Geo Maps (if coordinates exist)  

📌 Powered by **Plotly** for premium interactive visualizations

---

### 🧠 3. AI-Powered Analyst Summary
Powered by **Google Gemini**

Generates:
- Executive Bottom Line (The “So What?”)  
- KPI Breakdown  
- Trends & Patterns  
- Outliers & Anomalies  
- Correlations & Drivers  
- Business Recommendations  
- What-if Scenarios  

---

### 🧾 4. PDF Report Generation
- One-click download  
- Clean, structured report  

Includes:
- Dataset overview  
- KPIs  
- AI-generated insights  

📌 Built using **ReportLab**

---

### 🎯 5. Analyst-Level Insights (Not Basic AI)
Lumivise goes beyond simple dashboards:
- Thinks like a real data analyst  
- Explains:
  - Why a chart is used  
  - What it means in business terms  
- Highlights:
  - Risks  
  - Data quality issues  
  - Decision impact  

---

### 🎨 6. Premium UI/UX Dashboard
- Modern glassmorphism design  
- Smooth UI experience  
- Clean layout (inspired by Power BI)  
- Interactive sidebar filters  

---

## 🛠️ Tech Stack

| Category           | Tools        |
|------------------|-------------|
| Frontend         | Streamlit   |
| Visualization    | Plotly      |
| Backend Logic    | Python      |
| AI Engine        | Gemini API  |
| Data Processing  | Pandas      |
| Report Generation| ReportLab   |

---

## 📂 Project Structure

```
Lumivise/
│
├── main.py                # Main Streamlit app
├── chats/                 # Saved chat sessions
├── uploads/               # Uploaded datasets
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository
```bash
git clone "repo link"
cd lumivise
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Gemini API Key

Create file:
```
.streamlit/secrets.toml
```

Add:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

### 5. Run Application
```bash
streamlit run main.py
```

---

## 📥 How to Use

1. Upload a dataset (CSV / XLSX)  
2. Lumivise will automatically:
   - Clean the data  
   - Detect column types  
   - Generate visualizations  

3. Explore:
   - Dashboard  
   - Filters  
   - Charts with explanations  

4. View AI-generated summary  

5. Download PDF report 📄  

---

## ⚠️ Important Notes

For best results:
- Use **pre-cleaned datasets**

Lumivise does NOT:
- Force type conversions  
- Remove meaningful missing values  

Designed for:
- Data Analysts  
- Students  
- Business Users  

---

## 🧠 Example Use Cases

- Sales Analysis Dashboard  
- Marketing Performance Insights  
- Customer Segmentation  
- Financial Data Exploration  
- Academic Projects  

---

## 🚀 Future Improvements

- Multi-dataset comparison  
- Real-time data connections  
- Forecasting models  
- SQL database integration  
- Dashboard export (Power BI style)  

---

## 👩‍💻 Author

**Radhi Sri Bhavya Patamsetti**  
AI & Data Science Enthusiast  

- GitHub: https://github.com/BhavyaPatamsetti  
- LinkedIn: https://www.linkedin.com/in/bhavyapatamsetti/  

---

## ⭐ Final Thought

Lumivise is not just a dashboard -  
it’s a **thinking AI analyst** that explains your data like a human.
