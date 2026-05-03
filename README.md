🚀 Lumivise – AI Data Analyst Dashboard

Illuminate. Visualize. Summarize.

Lumivise is a premium AI-powered Business Intelligence (BI) dashboard generator that transforms raw datasets into interactive visualizations, analyst-grade insights, and executive-level summaries — all in one place.

It acts like a Personal AI Data Analyst:

Upload data → Get cleaned → Visualized → Explained → Summarized → Download report 📄

✨ Features

📊 1. Smart Data Processing
Safe cleaning (no destructive changes)
Removes:
Duplicate rows
Empty rows & columns
Preserves:
Original data types
Missing values (no blind filling)

📈 2. Automated Visualization Engine
Detects:
Numeric columns
Categorical columns
Date/time columns
Generates relevant charts only (no unnecessary plots):
Bar Charts
Line Charts
Scatter Plots
Histograms
Geo Maps (if coordinates exist)
Uses Plotly for premium interactive charts

🧠 3. AI-Powered Analyst Summary

Powered by Google Gemini

Generates:

Executive Bottom Line (So What?)
KPI Breakdown
Trends & Patterns
Outliers & Anomalies
Correlations & Drivers
Business Recommendations
What-if Scenarios

🧾 4. PDF Report Generation
One-click download
Clean, structured report
Includes:
Dataset overview
KPIs
AI insights
Built using ReportLab

🎯 5. Analyst-Level Insights (Not Basic AI)

Unlike basic dashboards, Lumivise:

Thinks like a real data analyst
Explains:
Why a chart is used
What it means in business terms
Highlights:
Risks
Data quality issues
Decision impact

🎨 6. Premium UI/UX Dashboard
Modern glassmorphism design
Smooth animations
Clean layout (like **Microsoft Power BI)
Sidebar filters (interactive)
🛠️ Tech Stack
Category	Tools
Frontend	Streamlit
Visualization	Plotly
Backend Logic	Python
AI Engine	Gemini API
Data Processing	Pandas
Report Generation	ReportLab

📂 Project Structure
Lumivise/
│
├── main.py                # Main Streamlit app
├── chats/                # Saved chat sessions
├── uploads/              # Uploaded datasets
├── requirements.txt
└── README.md


⚙️ Installation & Setup
1. Clone Repository
git clone "repo link"
cd lumivise

2. Create Virtual Environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Setup Gemini API Key
Create file:
.streamlit/secrets.toml
Add:
GEMINI_API_KEY = "your_api_key_here"

5. Run App
streamlit run main.py

📥 How to Use
Upload a dataset (CSV / XLSX)
Lumivise will:
Clean data safely
Detect columns
Generate visualizations
Explore:
Dashboard
Filters
Charts with explanations
View AI Summary
Download PDF Report 📄

⚠️ Important Notes
For best results:
Upload pre-cleaned dataset
Lumivise does NOT:
Force type conversions
Remove meaningful missing values
Designed for:
Analysts
Students
Business users

🧠 Example Use Cases
Sales Analysis Dashboard
Marketing Performance Insights
Customer Segmentation
Financial Data Exploration
Academic Projects

🚀 Future Improvements
Multi-dataset comparison
Real-time data connections
Forecasting models
SQL database integration
Dashboard export (Power BI style)

👩‍💻 Author
Radhi Sri Bhavya Patamsetti
AI & Data Science Enthusiast

GitHub: https://github.com/BhavyaPatamsetti
LinkedIn: https://www.linkedin.com/in/bhavyapatamsetti/

⭐ Final Thought
Lumivise is not just a dashboard -
it’s a thinking AI analyst that explains your data like a human.
