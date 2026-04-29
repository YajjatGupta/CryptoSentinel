import os
import requests
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.ensemble import IsolationForest
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import RobustScaler
from dotenv import load_dotenv
from plot_generator import plot_anomalies

try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None

try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
except ImportError:
    SARIMAX = None

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


def mean_absolute_percentage_error(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    non_zero = y_true != 0
    if not np.any(non_zero):
        return 0.0
    return np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100


def calculate_forecast_metrics(y_true, y_pred):
    return {
        'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
        'mae': float(mean_absolute_error(y_true, y_pred)),
        'mape': float(mean_absolute_percentage_error(y_true, y_pred)),
    }


def run_sarima_forecast(y_train, forecast_steps):
    if SARIMAX is None:
        return None, "statsmodels is not installed"

    seasonal_order = (1, 0, 1, 24) if len(y_train) >= 72 else (0, 0, 0, 0)
    model_label = "SARIMA(1,1,1)(1,0,1,24)" if seasonal_order != (0, 0, 0, 0) else "ARIMA(1,1,1)"

    try:
        y_train = y_train.dropna()
        if len(y_train) < 10:
            return None, f"{model_label} failed: not enough non-null training samples"

        # CoinGecko timestamps are not guaranteed to be perfectly regular, and pandas can lose
        # `.freq` through filtering operations. Statsmodels increasingly requires a supported
        # index with frequency for prediction/forecasting.
        if isinstance(y_train.index, pd.DatetimeIndex) and y_train.index.tz is not None:
            y_train = y_train.copy()
            y_train.index = y_train.index.tz_convert(None)

        freq = None
        if isinstance(y_train.index, pd.DatetimeIndex) and len(y_train.index) >= 3:
            freq = pd.infer_freq(y_train.index)
            if freq is None:
                deltas = np.diff(y_train.index.asi8)
                if deltas.size:
                    median_ns = int(np.median(deltas))
                    if median_ns > 0:
                        freq = pd.to_timedelta(median_ns, unit="ns")

        if freq is not None:
            regular_index = pd.date_range(start=y_train.index[0], periods=len(y_train), freq=freq)
            y_train = pd.Series(y_train.to_numpy(dtype=float), index=regular_index, name=y_train.name)

        model = SARIMAX(
            y_train,
            order=(1, 1, 1),
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fitted_model = model.fit(disp=False)
        forecast = fitted_model.forecast(steps=forecast_steps)
        return np.asarray(forecast, dtype=float), model_label
    except Exception as error:
        return None, f"{model_label} failed: {error}"


def build_advanced_forecaster(params=None):
    params = params or {}

    if XGBRegressor is not None:
        default_params = {
            'n_estimators': 350,
            'learning_rate': 0.03,
            'max_depth': 4,
            'subsample': 0.9,
            'colsample_bytree': 0.9,
        }
        default_params.update(params)

        return (
            XGBRegressor(
                **default_params,
                objective='reg:squarederror',
                random_state=42,
            ),
            "XGBoost Regressor",
            "Advanced Ensemble",
            default_params,
        )

    default_params = {
        'n_estimators': 250,
        'learning_rate': 0.04,
        'max_depth': 3,
        'subsample': 0.9,
    }
    default_params.update(params)

    return (
        GradientBoostingRegressor(
            **default_params,
            random_state=42,
        ),
        "Gradient Boosting Regressor",
        "Advanced Ensemble",
        default_params,
    )


def tune_advanced_forecaster(train_df, feature_columns):
    validation_size = max(12, int(len(train_df) * 0.2))
    if len(train_df) <= validation_size + 20:
        _model, model_name, model_type, params = build_advanced_forecaster()
        return params, model_name, model_type, []

    tuning_train = train_df.iloc[:-validation_size]
    validation_df = train_df.iloc[-validation_size:]

    if XGBRegressor is not None:
        param_grid = [
            {'n_estimators': 200, 'learning_rate': 0.03, 'max_depth': 3, 'subsample': 0.9, 'colsample_bytree': 0.9},
            {'n_estimators': 300, 'learning_rate': 0.03, 'max_depth': 4, 'subsample': 0.9, 'colsample_bytree': 0.9},
            {'n_estimators': 250, 'learning_rate': 0.05, 'max_depth': 3, 'subsample': 0.85, 'colsample_bytree': 0.9},
            {'n_estimators': 400, 'learning_rate': 0.02, 'max_depth': 4, 'subsample': 0.85, 'colsample_bytree': 0.85},
        ]
    else:
        param_grid = [
            {'n_estimators': 150, 'learning_rate': 0.05, 'max_depth': 2, 'subsample': 0.9},
            {'n_estimators': 250, 'learning_rate': 0.04, 'max_depth': 3, 'subsample': 0.9},
            {'n_estimators': 350, 'learning_rate': 0.03, 'max_depth': 3, 'subsample': 0.85},
        ]

    tuning_results = []
    best_params = None
    best_rmse = float('inf')
    best_model_name = None
    best_model_type = None

    for params in param_grid:
        model, model_name, model_type, resolved_params = build_advanced_forecaster(params)
        model.fit(tuning_train[feature_columns], tuning_train['target'])
        validation_pred = model.predict(validation_df[feature_columns])
        metrics = calculate_forecast_metrics(validation_df['target'], validation_pred)

        tuning_results.append({
            'model': model_name,
            'params': resolved_params,
            **metrics,
        })

        if metrics['rmse'] < best_rmse:
            best_rmse = metrics['rmse']
            best_params = resolved_params
            best_model_name = model_name
            best_model_type = model_type

    return best_params, best_model_name, best_model_type, tuning_results


def build_forecasting_frame(df, lag_count=12):
    forecast_df = df.copy()
    forecast_df.set_index('date', inplace=True)
    forecast_df.sort_index(inplace=True)
    forecast_df = forecast_df[~forecast_df.index.duplicated(keep='last')]
    forecast_df.ffill(inplace=True)

    forecast_df['return_1'] = forecast_df['value'].pct_change().replace([np.inf, -np.inf], np.nan)
    forecast_df['volume_change_1'] = forecast_df['volume'].pct_change().replace([np.inf, -np.inf], np.nan)
    forecast_df['rolling_mean_6'] = forecast_df['value'].rolling(6, min_periods=2).mean()
    forecast_df['rolling_std_6'] = forecast_df['value'].rolling(6, min_periods=2).std()
    forecast_df['rolling_volume_6'] = forecast_df['volume'].rolling(6, min_periods=2).mean()

    for lag in range(1, lag_count + 1):
        forecast_df[f'lag_{lag}'] = forecast_df['value'].shift(lag)

    forecast_df['target'] = forecast_df['value'].shift(-1)
    forecast_df = forecast_df.dropna()
    feature_columns = [
        *[f'lag_{lag}' for lag in range(1, lag_count + 1)],
        'volume',
        'return_1',
        'volume_change_1',
        'rolling_mean_6',
        'rolling_std_6',
        'rolling_volume_6',
    ]

    return forecast_df, feature_columns


def build_residual_frame(indexed_df, lag_count=12):
    residual_df = indexed_df.copy()

    for lag in range(1, lag_count + 1):
        residual_df[f'lag_{lag}'] = residual_df['value'].shift(lag)

    lagged_columns = [
        'volume',
        'return',
        'volume_change',
        'log_volume',
        'price_z',
        'volume_z',
        'volatility',
        'momentum',
    ]
    for column in lagged_columns:
        residual_df[f'prev_{column}'] = residual_df[column].shift(1)

    feature_columns = [
        *[f'lag_{lag}' for lag in range(1, lag_count + 1)],
        *[f'prev_{column}' for column in lagged_columns],
    ]
    residual_df['target'] = residual_df['value']
    residual_df = residual_df.dropna(subset=[*feature_columns, 'target'])

    return residual_df, feature_columns


def robust_normalize(series):
    median = series.median()
    iqr = series.quantile(0.75) - series.quantile(0.25)
    if iqr == 0 or pd.isna(iqr):
        iqr = series.std()
    if iqr == 0 or pd.isna(iqr):
        return pd.Series(0, index=series.index)
    return (series - median) / iqr


def add_forecast_residual_scores(model_df):
    model_df = model_df.copy()
    model_df['forecast_prediction'] = np.nan
    model_df['forecast_residual'] = np.nan
    model_df['forecast_residual_z'] = 0.0

    if len(model_df) < 60:
        return model_df

    residual_df, feature_columns = build_residual_frame(model_df)
    if len(residual_df) < 30:
        return model_df

    train_size = max(int(len(residual_df) * 0.7), len(residual_df) - max(18, int(len(residual_df) * 0.25)))
    train_df = residual_df.iloc[:train_size]
    score_df = residual_df.iloc[train_size:]

    if train_df.empty or score_df.empty:
        return model_df

    forecaster, _model_name, _model_type, _params = build_advanced_forecaster()
    forecaster.fit(train_df[feature_columns], train_df['target'])
    predictions = forecaster.predict(score_df[feature_columns])

    residuals = score_df['target'].to_numpy() - predictions
    rolling_sigma = model_df['value'].diff().rolling(24, min_periods=6).std()
    fallback_sigma = model_df['value'].diff().std()
    if fallback_sigma == 0 or pd.isna(fallback_sigma):
        fallback_sigma = 1.0
    rolling_sigma = rolling_sigma.reindex(score_df.index).fillna(fallback_sigma).replace(0, fallback_sigma)
    volatility_floor = score_df['target'].abs() * 0.005
    normalized_sigma = np.maximum(rolling_sigma.to_numpy(), volatility_floor.to_numpy())
    residual_z = np.clip(np.abs(residuals) / normalized_sigma, 0, 10)

    model_df.loc[score_df.index, 'forecast_prediction'] = predictions
    model_df.loc[score_df.index, 'forecast_residual'] = residuals
    model_df.loc[score_df.index, 'forecast_residual_z'] = residual_z

    return model_df


def run_forecast_comparison(df):
    if df.empty or len(df) < 60:
        raise ValueError("Not enough data for forecasting comparison. Try a longer time window.")

    model_df, feature_columns = build_forecasting_frame(df)
    if len(model_df) < 30:
        raise ValueError("Not enough prepared samples after feature engineering.")

    test_size = max(12, int(len(model_df) * 0.2))
    train_df = model_df.iloc[:-test_size]
    test_df = model_df.iloc[-test_size:]

    y_train = train_df['target']
    y_test = test_df['target']

    # Classical baseline: one-step naive forecast, a standard time-series benchmark.
    classical_pred = test_df['value'].to_numpy()
    sarima_pred, sarima_label = run_sarima_forecast(y_train, len(test_df))

    best_params, advanced_model_name, advanced_model_type, tuning_results = tune_advanced_forecaster(train_df, feature_columns)
    advanced_model, advanced_model_name, advanced_model_type, resolved_params = build_advanced_forecaster(best_params)
    advanced_model.fit(train_df[feature_columns], y_train)
    advanced_pred = advanced_model.predict(test_df[feature_columns])

    classical_metrics = calculate_forecast_metrics(y_test, classical_pred)
    sarima_metrics = calculate_forecast_metrics(y_test, sarima_pred) if sarima_pred is not None else None
    advanced_metrics = calculate_forecast_metrics(y_test, advanced_pred)

    comparison_rows = [
        {
            'model': 'Naive Last-Value Baseline',
            'type': 'Classical Baseline',
            **classical_metrics,
        },
    ]

    if sarima_metrics is not None:
        comparison_rows.append({
            'model': sarima_label,
            'type': 'Classical Time Series',
            **sarima_metrics,
        })
    else:
        comparison_rows.append({
            'model': 'SARIMA',
            'type': 'Classical Time Series',
            'status': sarima_label,
            'rmse': None,
            'mae': None,
            'mape': None,
        })

    comparison_rows.append({
            'model': advanced_model_name,
            'type': advanced_model_type,
            'tuned_params': resolved_params,
            **advanced_metrics,
        })

    valid_rows = [row for row in comparison_rows if row.get('rmse') is not None]
    best_model = min(valid_rows, key=lambda row: row['rmse'])['model']

    predictions = [
        {
            'date': index.isoformat(),
            'actual': float(actual),
            'classical_prediction': float(classical),
            'sarima_prediction': None if sarima_pred is None else float(sarima),
            'advanced_prediction': float(advanced),
        }
        for index, actual, classical, sarima, advanced in zip(
            test_df.index,
            y_test,
            classical_pred,
            sarima_pred if sarima_pred is not None else [None] * len(test_df),
            advanced_pred,
        )
    ]

    return {
        'comparison': comparison_rows,
        'best_model': best_model,
        'test_points': int(len(test_df)),
        'advanced_tuned_params': resolved_params,
        'tuning_results': tuning_results,
        'predictions': predictions,
    }


# Function to run anomaly detection
def run_anomaly_detection(df):
    if df.empty:
        return df, pd.DataFrame()

    df = df.copy()
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    df.ffill(inplace=True)

    model_df, feature_columns = build_model_features(df)
    model_df = add_forecast_residual_scores(model_df)
    scaled_features = RobustScaler().fit_transform(model_df[feature_columns])

    contamination = min(max(3 / len(model_df), 0.01), 0.025)
    model = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=42,
        max_samples='auto',
    )
    model.fit(scaled_features)

    model_df['isolation_score'] = -model.decision_function(scaled_features)
    isolation_component = robust_normalize(model_df['isolation_score']).clip(lower=0)
    residual_component = (model_df['forecast_residual_z'].fillna(0) / 3).clip(lower=0)
    volume_component = (model_df['volume_z'].abs().fillna(0) / 3).clip(lower=0)
    model_df['anomaly_score'] = isolation_component + residual_component + (0.35 * volume_component)

    score_threshold = model_df['anomaly_score'].quantile(0.985)
    rule_flag = (
        (model_df['price_z'].abs() >= 3.0)
        | (model_df['volume_z'].abs() >= 3.0)
        | (model_df['forecast_residual_z'] >= 3.0)
    )
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
                f"score {row['anomaly_score']:.3f}, residual-z {row.get('forecast_residual_z', 0):.2f}"
            )
            for index, row in recent.iterrows()
        ]

    sections = [
        "### Key Trends & Observations",
        f"* CryptoSentinel analyzed the latest 30 days of price and volume data for **{stock_code.capitalize()}**.",
        f"* The anomaly model flagged **{anomaly_count}** clustered anomaly events.",
        "* Scores combine Isolation Forest outlier detection, volatility-normalized forecast residuals, and rolling volume behavior.",
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
                    'isolation_score': float(row.get('isolation_score', 0)),
                    'forecast_residual': None if pd.isna(row.get('forecast_residual')) else float(row.get('forecast_residual')),
                    'forecast_residual_z': float(row.get('forecast_residual_z', 0)),
                    'severity': row.get('severity', 'Medium'),
                }
                for index, row in anomalies_df.iterrows()
            ],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forecast-comparison')
def forecast_comparison():
    stock_code = request.args.get('stock_code', 'bitcoin')
    days = int(request.args.get('days', 90))

    try:
        data_df = fetch_historical_data(stock_code, days=days)
        comparison = run_forecast_comparison(data_df)

        return jsonify({
            'asset': stock_code,
            'days': days,
            **comparison,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
