# AI-Powered Question Parsing Setup Guide

## Quick Start (No AI - Keyword Matching)

The dashboard already works with **keyword-based question parsing** - no setup needed!

Just type questions like:

- "What is the forecast for sales?"
- "Show me the correlation between revenue and customers"
- "Is the data stationary?"

The system will detect keywords and suggest relevant analyses.

---

## Advanced Setup (Google Gemini AI)

For **intelligent AI-powered question parsing**, follow these steps:

### Step 1: Get a Free Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### Step 2: Install Required Library

```bash
pip install google-generativeai
```

### Step 3: Configure API Key

**Option A: Environment Variable (Recommended)**

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set GEMINI_API_KEY=your-api-key-here

# Linux/Mac
export GEMINI_API_KEY="your-api-key-here"
```

**Option B: Enter in Dashboard**

1. Run the dashboard
2. Enable "AI Question Parsing" in the sidebar
3. Enter your API key in the text field

### Step 4: Use AI Features

1. **Enable AI Mode**: Check "Enable AI Question Parsing" in sidebar
2. **Ask Your Question**: Type your question in natural language
3. **Parse Question**: Click "🤖 Parse Question" button
4. **Review Suggestions**: AI will suggest relevant analyses and columns
5. **Run Analysis**: Click "🚀 Run Analysis" to execute

---

## Example Questions That Work Well

### Forecasting

- "Can you predict next week's sales?"
- "What will revenue look like in the future?"
- "Forecast customer demand for the next 7 days"

### Correlation

- "Are sales and revenue related?"
- "Show me how temperature affects demand"
- "What variables are correlated?"

### Stationarity

- "Is my time series stationary?"
- "Should I difference the data?"
- "Test for unit root"

### General Analysis

- "Give me an overview of the data"
- "What are the key statistics?"
- "Summarize the trends"

---

## How It Works

### Keyword Matching (No AI)

- Scans question for keywords like "forecast", "correlation", "stationary"
- Suggests relevant analyses based on matches
- Fast and works offline
- No API key needed

### Gemini AI (Advanced)

- Sends question to Google's Gemini AI
- AI understands context and intent
- Provides intelligent suggestions
- Returns explanations of what to expect
- Requires API key but free tier available

---

## Troubleshooting

### "google-generativeai not installed"

Run: `pip install google-generativeai`

### "Gemini API key not provided"

- Set the `GEMINI_API_KEY` environment variable, OR
- Enter API key in the dashboard sidebar

### AI parsing failed

- Dashboard will automatically fall back to keyword matching
- Check your API key is correct
- Ensure you have internet connection

---

## API Usage Limits

**Gemini Free Tier:**

- 60 requests per minute
- More than enough for dashboard usage
- No credit card required

For production use, consider upgrading to paid tier.

---

## Privacy Note

When using **keyword matching**: Data stays local, no external calls

When using **Gemini AI**:

- Your question is sent to Google's API
- Your actual data is NOT sent (only column names)
- Review Google's privacy policy for API usage
