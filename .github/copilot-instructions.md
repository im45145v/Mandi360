# Project: Mandi Customer Experience Intelligence

## Project Overview

This repository contains an academic Business Analytics project that builds an AI-driven Customer Experience Intelligence platform for ONE Mandi restaurant brand in Hyderabad, India.

The same system is designed to support two academic subjects:

1. Customer Relationship Management (CRM)
2. Data Mining and Predictive Analytics (DMPA)

The system analyzes real customer feedback collected from multiple branches of the same restaurant brand.

The project is NOT simply a sentiment-analysis application.

The intended analytical pipeline is:

Raw Customer Feedback
→ Data Ingestion
→ Validation
→ Cleaning
→ Sentiment Analysis
→ Aspect-Based Sentiment
→ Topic Mining
→ Clustering
→ Association Rule Mining
→ Anomaly Detection
→ Predictive Analytics
→ Agentic AI
→ CRM Insights and Recommendations
→ Streamlit Dashboard

## Core Research Goal

Determine how AI, data mining, predictive analytics, and agentic orchestration can convert unstructured customer feedback into actionable CRM intelligence.

## Important Academic Principle

The project must distinguish clearly between:

1. REAL DATA
   - Actual collected customer feedback
   - Actual ratings
   - Actual dates
   - Actual branch information

2. DERIVED DATA
   - Sentiment
   - Emotion
   - Topics
   - Aspects
   - Embeddings
   - Severity
   - Priority
   - Anomaly scores

3. PREDICTED DATA
   - Forecasted sentiment
   - Forecasted complaint volume
   - Branch risk
   - Priority probability
   - Other model predictions

4. SYNTHETIC/ASSUMED DATA
   - Only use when required
   - Must be explicitly labelled as synthetic or assumption-based
   - Never present synthetic observations as real customer data

Never fabricate research results, customer feedback, model metrics, or observations.

## Domain

The project focuses on ONE Mandi restaurant brand in Hyderabad.

Multiple branches of the same brand are analytical units.

Do NOT turn the main study into a comparison of unrelated restaurant brands unless explicitly requested.

The main hierarchy is:

Brand
→ Branch
→ Customer Feedback
→ Analytical Features
→ Insights

## Initial Data Source

The initial dataset will be an exported JSON file containing Google Maps review data.

Expected location:

data/raw/gmaps_reviews.json

The exact JSON schema is not known yet.

DO NOT assume the scraper's JSON structure.

First inspect the actual JSON structure and create a normalization layer.

Do not modify the raw JSON file.

## Data Handling

Raw data is immutable.

Never overwrite files under:

data/raw/

Normalized/cleaned data should be written to:

data/interim/

Final analytical datasets should be written to:

data/processed/

All transformations should be reproducible through Python code.

## Expected Normalized Review Schema

After ingestion, normalize records into a common schema where available:

- review_id
- brand_id
- branch_id
- branch_name
- source
- review_date
- rating
- review_text
- owner_response
- response_date
- review_url

Optional fields may exist.

Do not invent missing values.

Use null/None when information is unavailable.

## Branch Information

Branch-level analysis is important.

The system should support:

- branch performance
- branch sentiment
- branch topics
- branch aspect performance
- branch anomalies
- branch forecasts
- branch risk

Do not assume every review contains branch information.

Branch identification must be based on reliable source metadata or explicit mapping.

## Analytics

The project should eventually include:

### NLP

- text cleaning
- sentiment classification
- emotion detection where appropriate
- aspect extraction
- topic modeling

### Data Mining

- keyword/frequency analysis
- topic mining
- clustering
- association rule mining
- anomaly detection

### Predictive Analytics

- sentiment forecasting
- complaint/topic forecasting
- branch risk prediction
- priority/escalation prediction where a defensible target exists

## Model Selection Principle

Do not use an LLM for tasks that can be performed more appropriately using conventional statistics or machine learning.

Prefer:

- scikit-learn
- pandas
- numpy
- scipy
- statsmodels
- appropriate open-source NLP models

for deterministic/statistical/ML analytics.

Use OpenAI primarily for:

- agentic reasoning
- natural-language analysis
- insight synthesis
- CRM recommendations
- natural-language querying
- orchestration

## Agent Architecture

The initial agent architecture should remain small and understandable.

Core agents:

1. Orchestrator Agent
2. Insight/Investigation Agent
3. CRM Recommendation Agent

Do not create additional agents unless there is a clear responsibility that cannot be handled by an existing agent or deterministic analytical tool.

Agents should call analytical tools/functions instead of receiving entire datasets.

Examples of tools:

- get_brand_summary()
- get_branch_summary(branch_id)
- get_sentiment_trend(branch_id)
- get_top_topics(branch_id)
- get_aspect_sentiment(branch_id)
- get_anomalies()
- get_forecast(branch_id)
- get_association_rules()
- search_feedback(query)

## LLM Cost Control

Do NOT send the entire raw dataset to an LLM.

Do NOT call an LLM once per review unless explicitly justified.

Prefer:

Raw Data
→ Local/efficient NLP
→ Aggregation
→ Statistical/ML analysis
→ Small evidence package
→ LLM reasoning

The LLM should receive compact evidence rather than thousands of raw records.

## Reproducibility

Every important experiment should record:

- dataset version
- input features
- model
- parameters
- evaluation metrics
- output location

Important numerical results must be reproducible.

Never hardcode experimental results.

## Evaluation

Where applicable:

Sentiment:
- Accuracy
- Precision
- Recall
- F1

Clustering:
- Silhouette score
- Other appropriate clustering metrics

Association rules:
- Support
- Confidence
- Lift

Forecasting:
- MAE
- RMSE
- MAPE where appropriate

Classification:
- Precision
- Recall
- F1
- ROC-AUC where appropriate

Anomaly detection:
- Use suitable evaluation methods depending on whether ground-truth anomaly labels exist.

Do not invent ground-truth labels.

## Code Quality

Use Python.

Prefer modular functions over large scripts.

Use type hints where useful.

Use clear variable names.

Validate inputs.

Handle missing values explicitly.

Avoid global mutable state.

Avoid hardcoded API keys.

Use environment variables for secrets.

Add tests for important transformations and analytical functions.

Do not silently swallow exceptions.

## Database

Keep storage logic separate from analytics and UI.

The Streamlit application must not contain data-processing algorithms directly.

Analytics modules must be callable independently of Streamlit.

## Streamlit

Streamlit is the presentation layer.

Expected views:

- Executive Overview
- Sentiment
- Topics & Aspects
- Data Mining
- Predictive Analytics
- Anomaly Center
- Branch Intelligence
- AI Analyst

Do not put model-training logic directly into page files.

## Research Integrity

This is an academic research project.

Never:

- fabricate data
- fabricate model performance
- claim causation from correlation
- call a review fake without evidence
- claim a prediction is certain
- hide limitations
- present synthetic data as real
- present LLM-generated reasoning as ground truth

Clearly distinguish correlation, prediction, and causation.

## Development Process

Before implementing a major feature:

1. Inspect existing code.
2. Explain the proposed implementation.
3. Identify affected files.
4. Implement the smallest coherent change.
5. Run relevant tests.
6. Report what changed.
7. Report any assumptions.

Do not rewrite unrelated modules.

Do not introduce new frameworks or dependencies without justification.

## Current Development Priority

The immediate priority is:

1. Inspect the raw Google Maps JSON.
2. Understand its actual schema.
3. Build a robust JSON ingestion/normalization module.
4. Produce a normalized review dataset.
5. Validate the normalized dataset.
6. Only then begin NLP and analytics.

Do NOT implement the agentic layer yet.
Do NOT implement the Streamlit dashboard yet.
Do NOT implement predictive models yet.

The project must be built incrementally.
