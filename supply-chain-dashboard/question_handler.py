"""
Question Handler for AI-Powered Analysis
Supports both keyword-based parsing and Gemini API integration
"""

import re
from typing import List, Dict, Any


def parse_question_keywords(question: str, available_columns: List[str]) -> Dict[str, Any]:
    """
    Simple keyword-based question parser (no AI needed)
    Returns suggested analyses and relevant columns
    """
    question_lower = question.lower()
    
    suggestions = {
        'analyses': [],
        'columns': [],
        'insights': []
    }
    
    # Detect analysis types from keywords
    if any(word in question_lower for word in ['forecast', 'predict', 'future', 'next', 'trend']):
        suggestions['analyses'].append('📉 Forecasting (Moving Avg & SES)')
        suggestions['insights'].append("Detected forecasting request - will run Moving Average and SES models")
    
    if any(word in question_lower for word in ['correlat', 'relation', 'connect', 'depend']):
        suggestions['analyses'].append('🔗 Correlation Analysis')
        suggestions['insights'].append("Detected correlation request - will show relationships between variables")
    
    if any(word in question_lower for word in ['arima', 'time series', 'model']):
        suggestions['analyses'].append('🎯 ARIMA Modeling')
        suggestions['insights'].append("Detected ARIMA request - will fit time series model")
    
    if any(word in question_lower for word in ['stationary', 'adf', 'kpss', 'unit root']):
        suggestions['analyses'].append('📊 Stationarity Tests (ADF & KPSS)')
        suggestions['insights'].append("Detected stationarity test request")
    
    if any(word in question_lower for word in ['acf', 'pacf', 'autocorrelation', 'lag']):
        suggestions['analyses'].append('📐 ACF & PACF Plots')
        suggestions['insights'].append("Detected autocorrelation request")
    
    if any(word in question_lower for word in ['summary', 'overview', 'statistics', 'describe', 'mean', 'average']):
        suggestions['analyses'].append('📈 Exploratory Data Analysis (EDA)')
        suggestions['insights'].append("Detected statistical summary request")
    
    # Detect column mentions
    for col in available_columns:
        if col.lower() in question_lower:
            suggestions['columns'].append(col)
    
    # If no specific analyses detected, suggest EDA as default
    if not suggestions['analyses']:
        suggestions['analyses'].append('📈 Exploratory Data Analysis (EDA)')
        suggestions['insights'].append("No specific analysis detected - suggesting overview")
    
    return suggestions


def parse_question_with_gemini(question: str, available_columns: List[str], api_key: str = None) -> Dict[str, Any]:
    """
    Use Google Gemini API for intelligent question parsing
    Requires: pip install google-generativeai
    
    Args:
        question: User's question
        available_columns: List of available numeric columns
        api_key: Google Gemini API key (optional, can use environment variable)
    
    Returns:
        Dictionary with suggested analyses, columns, and AI response
    """
    try:
        import google.generativeai as genai
        import os
        
        # Configure API key
        if api_key:
            genai.configure(api_key=api_key)
        elif os.environ.get('GEMINI_API_KEY'):
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        else:
            raise ValueError("Gemini API key not provided")
        
        # Create the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt
        prompt = f"""You are a data analysis assistant. A user has a dataset with these numeric columns: {', '.join(available_columns)}

Available analyses:
1. Exploratory Data Analysis (EDA) - descriptive statistics
2. Correlation Analysis - relationships between variables
3. Forecasting - Moving Average and Simple Exponential Smoothing
4. Stationarity Tests - ADF and KPSS tests
5. ARIMA Modeling - time series forecasting
6. ACF & PACF Plots - autocorrelation analysis

User question: "{question}"

Based on the question, provide:
1. Which analyses are most relevant (list by name)
2. Which columns should be analyzed (from the available columns)
3. A brief explanation of what insights the user can expect

Format your response as:
ANALYSES: [comma-separated list]
COLUMNS: [comma-separated list]
EXPLANATION: [brief explanation]
"""
        
        # Generate response
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse the response
        suggestions = {
            'analyses': [],
            'columns': [],
            'insights': [],
            'ai_response': response_text
        }
        
        # Extract analyses
        if 'ANALYSES:' in response_text:
            analyses_line = response_text.split('ANALYSES:')[1].split('\n')[0].strip()
            # Map to our format
            analysis_mapping = {
                'EDA': '📈 Exploratory Data Analysis (EDA)',
                'Exploratory': '📈 Exploratory Data Analysis (EDA)',
                'Correlation': '🔗 Correlation Analysis',
                'Forecasting': '📉 Forecasting (Moving Avg & SES)',
                'Stationarity': '📊 Stationarity Tests (ADF & KPSS)',
                'ARIMA': '🎯 ARIMA Modeling',
                'ACF': '📐 ACF & PACF Plots',
                'PACF': '📐 ACF & PACF Plots'
            }
            for key, value in analysis_mapping.items():
                if key.lower() in analyses_line.lower() and value not in suggestions['analyses']:
                    suggestions['analyses'].append(value)
        
        # Extract columns
        if 'COLUMNS:' in response_text:
            columns_line = response_text.split('COLUMNS:')[1].split('\n')[0].strip()
            for col in available_columns:
                if col.lower() in columns_line.lower():
                    suggestions['columns'].append(col)
        
        # Extract explanation
        if 'EXPLANATION:' in response_text:
            explanation = response_text.split('EXPLANATION:')[1].strip()
            suggestions['insights'].append(explanation)
        
        return suggestions
        
    except ImportError:
        raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def get_ai_insights(question: str, available_columns: List[str], use_ai: bool = False, api_key: str = None) -> Dict[str, Any]:
    """
    Main function to get insights from user question
    
    Args:
        question: User's question
        available_columns: Available numeric columns
        use_ai: Whether to use Gemini API (if False, uses keyword matching)
        api_key: Optional Gemini API key
    
    Returns:
        Dictionary with suggested analyses, columns, and insights
    """
    if not question or not question.strip():
        return {
            'analyses': [],
            'columns': [],
            'insights': ['No question provided']
        }
    
    if use_ai:
        try:
            return parse_question_with_gemini(question, available_columns, api_key)
        except Exception as e:
            # Fallback to keyword-based if AI fails
            result = parse_question_keywords(question, available_columns)
            result['insights'].append(f"⚠️ AI parsing failed ({str(e)}), using keyword matching")
            return result
    else:
        return parse_question_keywords(question, available_columns)
