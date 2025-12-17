# 📊 Supply Chain Analytics Dashboard

An interactive Streamlit dashboard for comprehensive data analysis featuring exploratory data analysis (EDA), forecasting, correlation analysis, stationarity tests, and ARIMA modeling with optional AI-powered question parsing.

## ✨ Features

- **📈 Exploratory Data Analysis**: Descriptive statistics including mean, median, standard deviation, and coefficient of variation
- **🔗 Correlation Analysis**: Interactive heatmaps showing relationships between variables
- **📉 Forecasting**: 7-day Moving Average and Simple Exponential Smoothing predictions
- **📊 Stationarity Tests**: ADF (Augmented Dickey-Fuller) and KPSS statistical tests
- **🎯 ARIMA Modeling**: ARIMA(2,1,1) time series forecasting with train-test validation
- **📐 ACF & PACF Plots**: Autocorrelation and Partial Autocorrelation function visualization
- **🤖 AI Question Parsing**: Optional Google Gemini integration for natural language query understanding

## 🚀 Quick Start

### Installation

1. Clone this repository:

```bash
git clone https://github.com/jayaharshit/Antigravity.git
cd Antigravity/supply-chain-dashboard
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## 📋 Data Requirements

Your Excel file should contain:

- **Date column** (required): Date/datetime column for time series analysis
- **Numeric columns**: One or more numeric columns to analyze

Example data format:

| Date       | Sales | Revenue | Customers |
| ---------- | ----- | ------- | --------- |
| 2012-10-01 | 120   | 9500    | 85        |
| 2012-10-02 | 135   | 11000   | 92        |
| 2012-10-03 | 142   | 10500   | 88        |

The dashboard automatically detects and uses all numeric columns in your dataset!

## 🎯 Usage Guide

### Step 1: Upload Data

- Click "Upload Excel File" in the sidebar, or
- Click "🔄 Use Sample Data" to try with example data

### Step 2: Select Analyses

Choose one or more analyses from the dropdown:

- 📈 Exploratory Data Analysis (EDA)
- 🔗 Correlation Analysis
- 📉 Forecasting (Moving Avg & SES)
- 📊 Stationarity Tests (ADF & KPSS)
- 🎯 ARIMA Modeling
- 📐 ACF & PACF Plots

### Step 3: Select Column

For item-specific analyses (forecasting, ARIMA), select the numeric column you want to analyze

### Step 4: (Optional) Ask a Question

Type a natural language question about your data, such as:

- "What is the forecast for sales?"
- "Are sales and revenue correlated?"
- "Is my time series stationary?"

### Step 5: Run Analysis

Click "🚀 Run Analysis" to generate insights and visualizations

## 🤖 AI Features (Optional)

The dashboard includes optional AI-powered question parsing using Google Gemini.

### Setup

1. Get a free API key: https://makersuite.google.com/app/apikey

2. Enable AI mode in the sidebar and either:
   - Set environment variable: `GEMINI_API_KEY=your-api-key`
   - Enter the API key directly in the dashboard

For detailed AI setup instructions, see [AI_SETUP.md](AI_SETUP.md)

### Without AI

The dashboard works perfectly without AI using intelligent keyword matching!

## 📁 Project Structure

```
supply-chain-dashboard/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── dashboard.py                 # Main Streamlit application
├── analysis_engine.py           # Core analysis functions
├── question_handler.py          # AI question parsing logic
├── create_excel_template.py     # Sample data generator
├── sample_data_template.xlsx    # Example dataset
└── AI_SETUP.md                  # Detailed AI configuration guide
```

## 🔧 Creating Sample Data

Generate a sample Excel template:

```bash
python create_excel_template.py
```

This creates `sample_data_template.xlsx` with example data you can modify.

## 📊 Example Analyses

### Forecasting

Provides 7-day predictions using:

- **Moving Average**: Simple rolling average
- **Simple Exponential Smoothing**: Weighted exponential predictions

Metrics: RMSE and MAPE for accuracy evaluation

### Correlation Analysis

Visualizes relationships between all numeric variables using a color-coded heatmap

### Stationarity Tests

Determines if your time series is stationary using:

- **ADF Test**: Tests for unit root (null hypothesis: non-stationary)
- **KPSS Test**: Tests for stationarity (null hypothesis: stationary)

### ARIMA Modeling

Fits an ARIMA(2,1,1) model with:

- Train-test split (80/20)
- Performance metrics (RMSE, MAPE)
- Visual comparison of actual vs predicted values

## 🛠️ Troubleshooting

### "No module named 'streamlit'"

```bash
pip install -r requirements.txt
```

### Excel file read errors

Make sure you have `openpyxl` installed:

```bash
pip install openpyxl
```

### AI parsing not working

- Ensure `google-generativeai` is installed
- Check your API key is correct
- Dashboard will automatically fall back to keyword matching if AI fails

## 📝 License

This project is open source and available for educational and commercial use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👤 Author

**Harshit Jaya**

- GitHub: [@jayaharshit](https://github.com/jayaharshit)

## 🌟 Show your support

Give a ⭐️ if this project helped you!
