# 🏢 Real Estate Buyer Segmentation & Investment Profiling

📌 Project Overview

This project focuses on analyzing real estate buyers and their purchasing behavior to identify meaningful buyer segments using unsupervised machine learning. It combines buyer and property information to explore customer characteristics, investment preferences, property trends, and segment-level insights.

An interactive Streamlit dashboard presents the analysis through visualizations and filters, making buyer and property patterns easier to explore.

### 🛠️ Tech Stack

 Python |  Pandas |  Scikit-learn |Seaborn | Matplotlib| Plotly | Streamlit

### 📂 Project Files

- `client.csv` – Original client dataset.
- `property.csv` – Original property dataset.
- `buyer_property.csv` – Combined client and property data.
- `property_cluster.csv` – Client and property data with cluster labels.
- `Real_Estate_Buyer_Segmentation_and_Investment_Profiling.ipynb` – Data analysis, preprocessing, clustering, and buyer profiling.
- `app.py` – Interactive Streamlit dashboard.
- `kmeans_model.pkl` – Trained K-Means model.
- `encoder.pkl` – Saved categorical encoder.
- `scaler.pkl` – Saved numerical scaler.
- `requirements.txt` – Project dependencies.

### 🔍 Project Workflow

## 1. Data Preparation 

Inspected and prepared the client and property datasets.

Combined the datasets to connect buyer information with property records.

Encoded categorical variables and scaled numerical features for clustering.

## 2. Exploratory Data Analysis 📊

Examined buyer demographics, satisfaction scores, and acquisition purposes.

Explored property prices, sizes, and buyer–property relationships.

Analyzed purchasing and investment patterns across buyer groups.

## 3. Buyer Segmentation 

Applied K-Means Clustering to group buyers based on selected features.

Compared K-Means with Hierarchical Clustering using silhouette scores.

Assigned cluster labels and examined the characteristics of each segment.

## 4. Buyer Profiling 🏷️

Compared clusters based on age, satisfaction, acquisition purpose, and client type.

Explored differences in buyer characteristics and investment tendencies.

Connected buyer cluster labels to property records for further analysis.

## 5. Interactive Dashboard 🌐
The Streamlit dashboard supports interactive exploration of:

👥 Buyer segments and their characteristics

💰 Property prices and property-related metrics

🌍 Geographic patterns

📈 Investment and purchasing behavior

🔎 Segment-level insights using interactive filters

### 🔍 Key Features

- Data preprocessing and exploratory data analysis
- Buyer segmentation using K-Means clustering
- Comparison with Hierarchical Clustering
- Buyer cluster profiling and investment behavior analysis
- Interactive dashboard for buyer and property insights
