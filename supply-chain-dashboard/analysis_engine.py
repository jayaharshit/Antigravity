"""
Analysis Engine for Food Demand Analytics
Modular functions for different analysis types
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def validate_data(df):
    """Validate and prepare DataFrame - only Date column is required"""
    # Check for Date column
    if 'Date' not in df.columns:
        raise ValueError("Date column is required. Please ensure your dataset has a 'Date' column.")
    
    # Ensure Date is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    return df


def get_numeric_columns(df):
    """Get list of numeric columns (excluding Date)"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return numeric_cols


def get_available_items(df):
    """Get list of available numeric columns for analysis"""
    return get_numeric_columns(df)


def get_descriptive_stats(df):
    """Calculate descriptive statistics for all numeric columns"""
    items = get_numeric_columns(df)
    
    if not items:
        return pd.DataFrame()
    
    stats_data = []
    
    for item in items:
        mean_val = df[item].mean()
        median_val = df[item].median()
        std_val = df[item].std()
        cv_val = (std_val / mean_val) * 100 if mean_val != 0 else 0  # Coefficient of Variation
        min_val = df[item].min()
        max_val = df[item].max()
        
        stats_data.append({
            'Column': item,
            'Mean': round(mean_val, 2),
            'Median': round(median_val, 2),
            'Std Dev': round(std_val, 2),
            'CV (%)': round(cv_val, 2),
            'Min': min_val,
            'Max': max_val
        })
    
    return pd.DataFrame(stats_data)


def create_correlation_heatmap(df):
    """Create correlation heatmap for all numeric columns"""
    numeric_cols = get_numeric_columns(df)
    
    if len(numeric_cols) < 2:
        raise ValueError("Need at least 2 numeric columns for correlation analysis")
    
    correlation_matrix = df[numeric_cols].corr()
    
    # Adjust figure size based on number of columns
    fig_size = max(8, len(numeric_cols) * 0.8)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                fmt='.3f', square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Correlation Heatmap', 
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    return fig, correlation_matrix


def moving_average_forecast(series, window=7):
    """Calculate moving average forecast"""
    ma = pd.Series(series).rolling(window=window, center=False).mean()
    return ma


def simple_exponential_smoothing(series, alpha=0.2):
    """Perform Simple Exponential Smoothing"""
    ses_model = SimpleExpSmoothing(series)
    ses_fit = ses_model.fit(smoothing_level=alpha, optimized=False)
    return ses_fit.fittedvalues


def calculate_forecast_metrics(actual, predicted):
    """Calculate RMSE and MAPE for forecast"""
    # Remove NaN values
    mask = ~np.isnan(predicted)
    actual_clean = actual[mask]
    predicted_clean = predicted[mask]
    
    rmse = np.sqrt(mean_squared_error(actual_clean, predicted_clean))
    mape = mean_absolute_percentage_error(actual_clean, predicted_clean) * 100
    
    return {'RMSE': rmse, 'MAPE': mape}


def create_forecast_plot(df, item='Dosa', window=7, alpha=0.2):
    """Create forecast comparison plot"""
    series = df[item].values
    dates = df['Date'].values
    
    ma = moving_average_forecast(series, window)
    ses = simple_exponential_smoothing(series, alpha)
    
    # Calculate metrics
    valid_indices = np.arange(window, len(series))
    ma_metrics = calculate_forecast_metrics(series[valid_indices], ma[valid_indices])
    ses_metrics = calculate_forecast_metrics(series[1:], ses[1:])
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(dates, series, label=f'Actual {item} Demand', linewidth=2, alpha=0.8, color='#2E86AB')
    ax.plot(dates, ma, label=f'{window}-Day MA (RMSE: {ma_metrics["RMSE"]:.2f})', 
            linewidth=1.5, linestyle='--', color='#A23B72')
    ax.plot(dates, ses, label=f'SES α={alpha} (RMSE: {ses_metrics["RMSE"]:.2f})', 
            linewidth=1.5, linestyle='-.', color='#F18F01')
    
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Demand (Units)', fontsize=12, fontweight='bold')
    ax.set_title(f'{item} Demand Forecasting: Actual vs Moving Average vs SES', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig, {'MA': ma_metrics, 'SES': ses_metrics}


def perform_adf_test(series):
    """Perform Augmented Dickey-Fuller test"""
    result = adfuller(series)
    
    return {
        'statistic': result[0],
        'p_value': result[1],
        'critical_values': result[4],
        'is_stationary': result[1] < 0.05
    }


def perform_kpss_test(series):
    """Perform KPSS test"""
    result = kpss(series, regression='c', nlags='auto')
    
    return {
        'statistic': result[0],
        'p_value': result[1],
        'critical_values': result[3],
        'is_stationary': result[1] > 0.05
    }


def create_acf_pacf_plots(series, lags=30):
    """Create ACF and PACF plots"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # ACF Plot
    plot_acf(series, lags=lags, ax=axes[0], color='#2E86AB', alpha=0.7)
    axes[0].set_title('Autocorrelation Function (ACF)', fontsize=13, fontweight='bold', pad=15)
    axes[0].set_xlabel('Lag', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Autocorrelation', fontsize=11, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # PACF Plot
    plot_pacf(series, lags=lags, ax=axes[1], color='#A23B72', alpha=0.7)
    axes[1].set_title('Partial Autocorrelation Function (PACF)', fontsize=13, fontweight='bold', pad=15)
    axes[1].set_xlabel('Lag', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Partial Autocorrelation', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def fit_arima_model(series, order=(2, 1, 1), train_ratio=0.8):
    """Fit ARIMA model and return forecast"""
    train_size = int(len(series) * train_ratio)
    train_data = series[:train_size]
    test_data = series[train_size:]
    
    # Fit model
    model = ARIMA(train_data, order=order)
    fit = model.fit()
    
    # Forecast
    n_forecast = len(test_data)
    forecast = fit.forecast(steps=n_forecast)
    
    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(test_data, forecast))
    mape = mean_absolute_percentage_error(test_data, forecast) * 100
    
    return {
        'model': fit,
        'forecast': forecast,
        'train_data': train_data,
        'test_data': test_data,
        'train_size': train_size,
        'rmse': rmse,
        'mape': mape,
        'summary': fit.summary()
    }


def create_arima_plot(df, item='Dosa', order=(2, 1, 1), train_ratio=0.8):
    """Create ARIMA forecast plot"""
    series = df[item].values
    dates = df['Date'].values
    
    result = fit_arima_model(series, order, train_ratio)
    
    train_size = result['train_size']
    train_dates = dates[:train_size]
    test_dates = dates[train_size:]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot training data
    ax.plot(train_dates, result['train_data'], label='Training Data', 
            linewidth=2, color='#2E86AB', alpha=0.7)
    
    # Plot actual test data
    ax.plot(test_dates, result['test_data'], label='Actual Test Data', 
            linewidth=2, color='#0D1B2A', marker='o', markersize=4)
    
    # Plot ARIMA forecast
    ax.plot(test_dates, result['forecast'], 
            label=f'ARIMA{order} Forecast (RMSE: {result["rmse"]:.2f})', 
            linewidth=2, linestyle='--', color='#F18F01', marker='s', markersize=4)
    
    ax.axvline(x=train_dates[-1], color='red', linestyle=':', linewidth=1.5, 
               label='Train-Test Split', alpha=0.7)
    
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'{item} Demand (Units)', fontsize=12, fontweight='bold')
    ax.set_title(f'ARIMA{order} Forecast vs Actual - {item} Demand', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig, result
