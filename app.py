import os
import requests
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from dotenv import load_dotenv
from plot_generator import plot_anomalies

# Load environment variables from .env file
load_dotenv()

# Configure Flask app and CORS
app = Flask(__name__)
CORS(app)

print("CryptoSentinel backend ready. Using local anomaly summaries.")

# List of cryptocurrencies from main.ipynb
TOP_5_COINS = ['bitcoin', 'ethereum', 'ripple', 'cardano', 'solana']

# Function to fetch historical data from CoinGecko
def fetch_historical_data(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    
    if coin_id not in TOP_5_COINS:
        raise ValueError(f"Invalid coin_id: {coin_id}")

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        timestamps = [item[0] for item in data['prices']]
        prices = [item[1] for item in data['prices']]
        volumes = [item[1] for item in data['total_volumes']]

        df = pd.DataFrame({
            'date': pd.to_datetime(timestamps, unit='ms'),
            'value': prices,
            'volume': volumes
        })
        
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()
    except KeyError:
        print(f"API response for {coin_id} is missing expected keys.")
        return pd.DataFrame()

def build_model_features(df):
    model_df = df.copy()
    model_df['return'] = model_df['value'].pct_change().replace([np.inf, -np.inf], np.nan)
    model_df['log_return'] = np.log(model_df['value']).diff().replace([np.inf, -np.inf], np.nan)
    model_df['volume_change'] = model_df['volume'].pct_change().replace([np.inf, -np.inf], np.nan)
    model_df['log_volume'] = np.log1p(model_df['volume'])

    rolling_window = 24 if len(model_df) >= 72 else max(5, len(model_df) // 4)
    price_mean = model_df['value'].rolling(rolling_window, min_periods=3).mean()
    price_std = model_df['value'].rolling(rolling_window, min_periods=3).std()
    volume_mean = model_df['volume'].rolling(rolling_window, min_periods=3).mean()
    volume_std = model_df['volume'].rolling(rolling_window, min_periods=3).std()

    model_df['price_z'] = (model_df['value'] - price_mean) / price_std.replace(0, np.nan)
    model_df['volume_z'] = (model_df['volume'] - volume_mean) / volume_std.replace(0, np.nan)
    model_df['volatility'] = model_df['log_return'].rolling(rolling_window, min_periods=3).std()
    model_df['momentum'] = model_df['value'].pct_change(rolling_window).replace([np.inf, -np.inf], np.nan)

    feature_columns = [
        'log_return',
        'volume_change',
        'log_volume',
        'price_z',
        'volume_z',
        'volatility',
        'momentum',
    ]
    model_df[feature_columns] = model_df[feature_columns].fillna(0)
    return model_df, feature_columns


def severity_from_score(score, quantiles):
    if score >= quantiles[0.99]:
        return "Critical"
    if score >= quantiles[0.975]:
        return "High"
    if score >= quantiles[0.95]:
        return "Medium"
    return "Low"


def cluster_anomaly_events(df, max_gap='6h'):
    candidates = df[df['anomaly_candidate']].copy()
    if candidates.empty:
        return candidates

    selected_indices = []
    cluster = []
    previous_index = None
    max_gap_delta = pd.Timedelta(max_gap)

    for index, _row in candidates.iterrows():
        if previous_index is None or index - previous_index <= max_gap_delta:
            cluster.append(index)
        else:
            selected_indices.append(candidates.loc[cluster, 'anomaly_score'].idxmax())
            cluster = [index]
        previous_index = index

    if cluster:
        selected_indices.append(candidates.loc[cluster, 'anomaly_score'].idxmax())

    return df.loc[selected_indices].sort_index()


# Function to run anomaly detection
def run_anomaly_detection(df):
    if df.empty:
        return df, pd.DataFrame()

    df = df.copy()
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    df.ffill(inplace=True)

    model_df, feature_columns = build_model_features(df)
    scaled_features = RobustScaler().fit_transform(model_df[feature_columns])

    contamination = min(max(3 / len(model_df), 0.01), 0.025)
    model = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=42,
        max_samples='auto',
    )
    model.fit(scaled_features)

    model_df['anomaly_score'] = -model.decision_function(scaled_features)
    score_threshold = model_df['anomaly_score'].quantile(0.985)
    rule_flag = (model_df['price_z'].abs() >= 3.0) | (model_df['volume_z'].abs() >= 3.0)
    model_df['anomaly_candidate'] = (model_df['anomaly_score'] >= score_threshold) | rule_flag

    quantiles = model_df['anomaly_score'].quantile([0.95, 0.975, 0.99]).to_dict()
    model_df['severity'] = model_df['anomaly_score'].apply(lambda score: severity_from_score(score, quantiles))
    model_df['anomaly'] = False

    anomalies = cluster_anomaly_events(model_df)
    if not anomalies.empty:
        model_df.loc[anomalies.index, 'anomaly'] = True
        anomalies = model_df.loc[anomalies.index]

    return model_df, anomalies

def build_local_analysis(stock_code, anomalies_df):
    anomaly_count = len(anomalies_df)
    latest_lines = ["* No anomalies were detected in the latest 30 day window."]

    if anomaly_count:
        recent = anomalies_df.sort_values('anomaly_score', ascending=False).head(5).sort_index()
        latest_lines = [
            (
                f"* {index.strftime('%b %d, %Y %H:%M')}: **{row.get('severity', 'Medium')}** signal, "
                f"price ${row['value']:,.2f}, volume {row['volume']:,.0f}, "
                f"score {row['anomaly_score']:.3f}"
            )
            for index, row in recent.iterrows()
        ]

    sections = [
        "### Key Trends & Observations",
        f"* CryptoSentinel analyzed the latest 30 days of price and volume data for **{stock_code.capitalize()}**.",
        f"* The anomaly model flagged **{anomaly_count}** clustered anomaly events.",
        "* Scores combine statistical outlier detection with rolling price and volume behavior.",
        "",
        "### Anomaly Breakdown",
        *latest_lines,
        "",
        "### Recommended Actions",
        "* Review the highlighted dates before entering a position.",
        "* Compare the signal with news, exchange activity, and wider market movement.",
        "* Prioritize High and Critical signals for manual review.",
        "* Treat anomaly flags as investigation prompts, not buy or sell instructions.",
        "",
        "**This analysis is generated by CryptoSentinel's anomaly pipeline for educational purposes and is not financial advice. Do your own research.**",
    ]

    return "\n".join(sections)

@app.route('/pred/<path:filename>')
def prediction_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'public', 'pred'), filename)

@app.route('/api/analyze-crypto')
def analyze_crypto():
    stock_code = request.args.get('stock_code', 'bitcoin')
    
    try:
        data_df, anomalies_df = run_anomaly_detection(fetch_historical_data(stock_code, days=30))
        
        # Generate and save the plot image
        plot_path = plot_anomalies(data_df, stock_code, anomalies_df)
        
        analysis = build_local_analysis(stock_code, anomalies_df)
        
        return jsonify({
            'image_path': f"/pred/{os.path.basename(plot_path)}",
            'analysis': analysis,
            'anomaly_count': int(len(anomalies_df)),
            'anomalies': [
                {
                    'date': index.isoformat(),
                    'price': float(row['value']),
                    'volume': float(row['volume']),
                    'score': float(row['anomaly_score']),
                    'severity': row.get('severity', 'Medium'),
                }
                for index, row in anomalies_df.iterrows()
            ],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
