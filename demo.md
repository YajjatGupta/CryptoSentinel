# CryptoSentinel: AI-Driven Web3 Security
Welcome to the CryptoSentinel demo! This guide will walk you through a core feature of our platform: AI-powered market anomaly detection and analysis.

## How It Works
Our platform uses machine learning models to analyze cryptocurrency price and volume data. The app.py backend fetches historical data for a selected coin using the CoinGecko API, then runs an Isolation Forest model to detect anomalies. The detected anomalies are then visualized on a chart, and the Google Gemini API is used to generate a detailed, human-readable analysis of the findings.

## Demo Steps
Backend Initialization: The Flask server is the core of our backend. To start it, you can run python app.py. The server is configured to use your GEMINI_API_KEY from the .env file. It will run on http://localhost:5000.

## Frontend Interface:
The frontend is a React application built with Vite and Tailwind CSS. The dashboard page, located at /dashboard, allows you to select a cryptocurrency from a dropdown menu. The list of available coins is defined in the Dashboard.tsx file and includes: bitcoin, ethereum, ripple, cardano, and solana.

## Viewing the Analysis:
When you select a coin, the frontend makes an API call to the backend. The backend processes the data, generates a chart showing price, volume, and any detected anomalies (marked by red dots). It then generates an AI analysis of the chart and sends both the chart image and the analysis text back to the frontend. The chart is displayed in the main content area, and the AI analysis is rendered below it in a dedicated card component.

## Interpreting the Results: 
The AI analysis is structured into three sections: "Key Trends & Observations," "Anomaly Breakdown," and "Recommended Actions". This provides a clear and actionable summary of the AI's findings. A critical disclaimer is always included at the end: "This is an AI-generated analysis for educational purposes on a platform called CryptoSentinel and is not financial advice. Do your own research.".