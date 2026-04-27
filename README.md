# CryptoSentinel

CryptoSentinel is a Web3 market surveillance dashboard for detecting unusual crypto price and volume activity. It combines a React website with a Flask API that fetches CoinGecko market data, runs anomaly detection, generates charts, and returns a Markdown anomaly summary.

The frontend also works without the Flask server by showing saved demo charts from `public/pred`.

## Features

- Landing website with Home, Features, Pricing, Contact, Login, Signup, and Dashboard pages.
- Demo dashboard with saved crypto anomaly charts.
- Optional live Flask backend for Bitcoin, Ethereum, Ripple, Cardano, and Solana analysis.
- Isolation Forest anomaly detection using price and volume.
- Matplotlib chart generation into `public/pred`.
- Model-ready backend structure so you can plug in your own analysis model.
- Mock authentication using React Context and `localStorage`.
- Light/dark theme support.

## Tech Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, shadcn-ui, React Router.
- Backend: Python, Flask, Flask-CORS.
- Data: CoinGecko market chart API.
- ML/Analysis: scikit-learn Isolation Forest.
- Charts: Matplotlib.
- Analysis output: local anomaly summary, ready to replace with a custom model.

## Project Structure

```text
CryptoSentinel/
  public/
    pred/                 Saved and generated analysis charts
    favicon.png
    lg.png
    logo.png
  src/
    components/
      auth/
      dashboard/
      home/
      layout/
      ui/
    contexts/
    hooks/
    lib/
    pages/
    App.tsx
    main.tsx
  app.py                  Flask API server
  plot_generator.py       Chart generation helper
  Graph.py                Experimental/alternative analysis script
  requirements.txt        Python backend dependencies
  package.json            Frontend dependencies and scripts
  vite.config.ts          Vite configuration
```

## Prerequisites

- Node.js 18 or newer.
- Python 3.10 or newer.
- Internet access for npm/pip install and live CoinGecko data.

## Run The Website

From the project folder:

```bash
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:8080
```

The dashboard is available at:

```text
http://127.0.0.1:8080/dashboard
```

## Run The Backend

Open a second terminal in the same project folder:

```bash
pip install -r requirements.txt
python app.py
```

The Flask API runs on:

```text
http://localhost:5000
```

Live dashboard analysis uses:

```text
GET http://localhost:5000/api/analyze-crypto?stock_code=bitcoin
```

Supported `stock_code` values:

```text
bitcoin
ethereum
ripple
cardano
solana
```

## Current Detection Model

The backend model lives in `app.py`:

- Fetches 30 days of CoinGecko price and volume data.
- Builds model features from log returns, volume changes, rolling price/volume z-scores, volatility, and momentum.
- Uses `RobustScaler` so extreme crypto spikes do not distort the whole feature space.
- Runs `IsolationForest` with adaptive contamination instead of forcing a fixed 5% anomaly rate.
- Adds rule-based flags for large rolling price or volume shocks.
- Clusters nearby suspicious points into single anomaly events so hourly data does not spam the dashboard.
- Assigns severity labels: Low, Medium, High, Critical.

To plug in your own model, replace or extend `run_anomaly_detection()` while keeping its return shape:

```python
return scored_dataframe, anomalies_dataframe
```

The `anomalies_dataframe` should include `value`, `volume`, `anomaly_score`, and `severity` columns so the chart and API response continue to work.

## Environment Variables

Copy `.env.example` to `.env` if you want to point the frontend at a different backend URL:

```bash
copy .env.example .env
```

```env
VITE_API_BASE_URL=http://localhost:5000
```

## Build

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Troubleshooting

- If PowerShell blocks `npm`, use `npm.cmd install` and `npm.cmd run dev`.
- If the dashboard says it is using saved demo data, start the Flask backend with `python app.py`.
- If `pip install -r requirements.txt` times out, rerun it when the network is stable. The frontend still runs without the backend.

## Team

- Shubham Tandon - Roll No. e23cseu1730
- Vihag Chaturvedi - Roll No. e23eceu0005
- Vipin Yadav - Roll No. e23cseu1728
- Yajat Gupta - Roll No. e23cseu1881

## License

[MIT](https://choosealicense.com/licenses/mit/)
