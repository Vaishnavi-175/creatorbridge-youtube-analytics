# CreatorBridge | YouTube Creator & Brand Analytics Platform

### Turning Creator Data into Smarter Marketing Decisions

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=postgresql&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

**CreatorBridge** is a data-driven analytics project designed to help brands evaluate YouTube creators, understand audience patterns, and analyze influencer marketing campaign performance.

By combining Python-based data processing, SQL concepts, a Streamlit application, and interactive Power BI dashboards, CreatorBridge demonstrates how raw creator and campaign metrics can be transformed into meaningful business insights.

> **Project Focus:** Creator Performance Analytics | Influencer Marketing | Campaign Measurement | Data Visualization

---

## 📊 Dashboard Preview

CreatorBridge features four Power BI dashboard pages covering executive-level metrics, creator performance, campaign analytics, and audience insights.

### 1. Executive Dashboard

A high-level overview of key creator and campaign performance indicators.

![Executive Dashboard](screenshots/executive_dashboard.png)

### 2. Creator Performance

Compare creator scores, engagement rates, average views, and category-level performance.

![Creator Performance](screenshots/Creater%20Performance.png)

### 3. Campaign Analytics

Explore campaign views, clicks, conversions, and conversion-rate metrics.

![Campaign Analytics](screenshots/Campaign%20Analytics.png)

### 4. Audience Insights

Analyze creator distribution by language and category, along with subscriber-related metrics.

![Audience Insights](screenshots/Audience%20Insights.png)

---

## 🎯 Business Problem

Brands often face challenges when selecting YouTube creators for influencer marketing campaigns. Subscriber counts alone do not fully explain engagement quality, audience relevance, or campaign effectiveness.

CreatorBridge explores a structured, analytics-driven approach to these challenges by bringing creator metrics, audience indicators, and campaign performance measures into one project.

### Project Objectives

- Evaluate and compare YouTube creator performance.
- Analyze engagement rates, views, and subscriber counts.
- Compare creator performance across categories and languages.
- Measure campaign reach, clicks, conversions, and conversion rates.
- Develop a calculated scoring approach for creator comparison.
- Present business insights through interactive Power BI dashboards.
- Provide a Python-based interface for exploring analytics.

---

## ✨ Key Features

### 👤 Creator Performance Analytics

- Creator-level performance comparison.
- Engagement-rate and average-views analysis.
- CreatorBridge Score-based ranking.
- Category-level performance comparisons.
- Identification of creators with stronger measured performance.

### 📈 Campaign Analytics

- Campaign views, clicks, and conversions analysis.
- Creator-level campaign comparisons.
- Conversion-rate analysis.
- Campaign score comparisons.
- Performance indicators to support marketing evaluation.

### 🌍 Audience Insights

- Creator distribution by language.
- Creator distribution by category.
- Subscriber analysis across categories.
- Comparison of creator categories across languages.
- Creator-level audience and profile overview.

### 📊 Interactive Power BI Dashboards

The Power BI report contains four pages:

| Dashboard Page | Purpose |
|---|---|
| Executive Dashboard | Overall performance overview |
| Creator Performance | Creator comparison and engagement analysis |
| Campaign Analytics | Campaign metrics and conversion analysis |
| Audience Insights | Category, language, and subscriber insights |

### 🐍 Python & Streamlit Application

The project includes a Streamlit application and Python utilities for exploring project analytics and supporting application-level data validation.

---

## 🛠️ Technology Stack

| Technology | Application |
|---|---|
| Python | Data processing, analysis, and application development |
| Pandas | Data manipulation and transformation |
| SQL | Data querying and analytical database concepts |
| Power BI | Interactive dashboards and business intelligence |
| Streamlit | Python-based analytics interface |
| Jupyter Notebook | Data generation and experimentation |
| Git & GitHub | Version control and project collaboration |

---

## 🧮 CreatorBridge Scoring Approach

CreatorBridge incorporates calculated metrics to support creator and campaign comparisons.

The project dataset includes:

- **Creator Performance Score** — a creator-level performance indicator.
- **Campaign Score** — a metric for campaign-level comparison.
- **CreatorBridge Score** — a combined project scoring indicator.

These metrics help organize creator comparisons into a structured analytical framework. Their interpretation depends on the underlying formulas and available data; a higher score does not guarantee better results for every brand or campaign.

---

## 📁 Project Structure

```text
CreatorBridge/
│
├── data/                  # Project datasets and generated data
├── documentation/         # Project documentation
├── powerbi/               # Power BI dashboard report
├── python/                # Python notebooks and analysis
├── screenshots/           # Dashboard preview images
├── sql/                   # SQL scripts and queries
├── tests/                 # Project tests
├── web/                   # Streamlit application
│   ├── app.py
│   └── utils/
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🚀 Getting Started

Follow these steps to run the project locally.

### Prerequisites

- Python installed on your system.
- Git installed on your system.
- Power BI Desktop to open the `.pbix` report.
- Project dependencies listed in `requirements.txt`.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Vaishnavi-175/creatorbridge-youtube-analytics.git
cd creatorbridge-youtube-analytics
```

### Step 2: Create a Virtual Environment

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Run the Streamlit Application

```bash
streamlit run web/app.py
```

The application will display a local URL in the terminal. Open that URL in your browser.

### Step 5: Open the Power BI Dashboard

Open this report in Power BI Desktop:

[`CreatorBridge_YouTube_Analytics_Dashboard.pbix`](powerbi/CreatorBridge_YouTube_Analytics_Dashboard.pbix)

**Note:** Successful execution depends on the availability of the required datasets, compatible package versions, and correctly configured file paths.

---

## 💡 Business Questions Explored

CreatorBridge is designed to help explore questions such as:

1. Which creators have stronger engagement relative to their audience size?
2. How does creator performance vary across categories?
3. Which creators generate higher campaign views and clicks?
4. How do campaign conversions and conversion rates compare?
5. How are creators distributed across languages and categories?
6. How can multiple performance indicators support creator selection?
7. Which metrics should brands consider when evaluating creator partnerships?

---

## 📌 Key Analytical Areas

The project brings together several dimensions of data analysis:

- **Descriptive Analytics:** Understand creator and campaign performance.
- **Comparative Analytics:** Compare creators, categories, and campaigns.
- **Performance Measurement:** Review engagement and conversion indicators.
- **Data Visualization:** Communicate findings through Power BI dashboards.
- **Application Development:** Explore analytics through a Streamlit interface.

---

## 📂 Data & Methodology

The project uses structured creator, video, and campaign metrics for analytical exploration.

Where generated or synthetic data is used, the results are intended for demonstration, testing, and methodology development. They should not be interpreted as verified real-world creator statistics or campaign outcomes.

Creator scores and conversion metrics should be evaluated alongside their calculation methods and underlying data. Real-world business use would require appropriate data validation and testing.

---

## 🔮 Future Improvements

Potential areas for further development include:

- Automated data ingestion from reliable sources.
- Expanded data quality checks and automated testing.
- Clearer documentation of scoring formulas.
- Additional creator discovery and filtering capabilities.
- Improved application deployment and performance.
- Evaluation using validated real-world campaign data.

---

## 👩‍💻 About the Project

CreatorBridge is a portfolio project exploring how data analytics and business intelligence can support influencer marketing decisions.

It demonstrates practical work across data preparation, analytical metrics, scoring concepts, interactive visualization, and Python application development.

**Developed by Vaishnavi**

- GitHub: [@Vaishnavi-175](https://github.com/Vaishnavi-175)
- Repository: [CreatorBridge – YouTube Creator & Brand Analytics](https://github.com/Vaishnavi-175/creatorbridge-youtube-analytics)

---

### ⭐ CreatorBridge

*Connecting creator insights with smarter brand decisions.*

