# CreatorBridge – Data Sources & Data Strategy

## Overview

CreatorBridge uses a hybrid data strategy combining publicly available creator/video data with simulated business campaign data.

The purpose is to build a realistic end-to-end analytics case study while clearly distinguishing observed data from generated business scenarios.

---

## 1. Creator & Channel Data

Source type:

- Publicly available YouTube channel/video information
- Public datasets and/or API-style structured data

Potential fields:

- Channel name
- Creator category
- Subscribers
- Total views
- Video count
- Upload dates
- Video titles
- Video type

---

## 2. Video Performance Data

Source type:

- Publicly available video-level performance data

Metrics:

- Views
- Likes
- Comments
- Shares
- Watch time where available

Derived metrics:

- Engagement rate
- Average views per video
- Like rate
- Comment rate
- Performance trend

---

## 3. Audience Data

Source type:

- Publicly available audience information where available
- Realistic simulated demographic data where public data is unavailable

Metrics:

- Age group
- Gender
- Location
- Audience percentage

---

## 4. Brand Data

Source type:

- Simulated business dataset

Purpose:

Brand information is created to represent realistic business scenarios for analytics.

Fields include:

- Brand
- Product
- Category

---

## 5. Campaign Data

Source type:

- Simulated campaign dataset

Purpose:

Campaign data is generated to demonstrate business analytics such as:

- Campaign budget
- Creator cost
- Views
- Clicks
- Conversions
- Revenue
- ROI

---

## 6. Why a Hybrid Dataset?

A creator analytics platform requires both creator-side performance data and business-side campaign outcome data.

Public creator data can provide realistic content and performance signals, while campaign and revenue data generally requires private business information.

Therefore, simulated campaign data is used where real business data is unavailable.

---

## 7. Data Transparency

CreatorBridge will clearly label simulated or generated data.

The project will not claim that simulated campaign results represent real brand campaigns or real business transactions.

---

## 8. Data Quality Checks

Before analysis, the datasets will be checked for:

- Missing values
- Duplicate records
- Invalid dates
- Invalid numeric values
- Inconsistent categories
- Referential integrity
- Outliers
- Impossible metric combinations

---

## 9. Data Pipeline

Raw Data
→ Data Cleaning
→ Data Validation
→ Data Modeling
→ SQL Analysis
→ Python Analysis
→ Analytics Layer
→ Power BI
→ Web Application