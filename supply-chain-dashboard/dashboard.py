"""
Interactive Dashboard for Food Demand Analysis
Upload Excel files, select analyses, and get instant results
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import analysis_engine as ae
import question_handler as qh

# Page configuration
st.set_page_config(
    page_title="Food Demand Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 SCA Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your data, select analyses, and get instant insights</div>', unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Sidebar - File Upload and Configuration
with st.sidebar:
    st.header("📁 Data Upload")
    
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload any Excel file with a Date column and numeric data columns"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df = ae.validate_data(df)
            st.session_state.df = df
            st.session_state.available_items = ae.get_available_items(df)
            st.success(f"✅ File loaded: {len(df)} records")
            st.info(f"📅 Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.session_state.df = None
            st.session_state.available_items = []
    
    # Use sample data option
    st.markdown("---")
    if st.button("🔄 Use Sample Data"):
        try:
            sample_path = "sample_data_template.xlsx"
            df = pd.read_excel(sample_path)
            df = ae.validate_data(df)
            st.session_state.df = df
            st.session_state.available_items = ae.get_available_items(df)
            st.success("✅ Sample data loaded!")
        except Exception as e:
            st.warning("Sample data not found. Please upload your own file.")
    
    st.markdown("---")
    if st.session_state.df is not None:
        st.markdown("### 📊 Dataset Info")
        st.markdown(f"**Columns:** {len(st.session_state.df.columns)}")
        numeric_cols = ae.get_numeric_columns(st.session_state.df)
        st.markdown(f"**Numeric Columns:** {len(numeric_cols)}")
        with st.expander("View All Columns"):
            for col in st.session_state.df.columns:
                col_type = "📊 Numeric" if col in numeric_cols else "📝 Other"
                st.markdown(f"- {col_type} `{col}`")
    else:
        st.markdown("### 📋 Requirements")
        st.markdown("""
        - `Date` column (required)
        - Any numeric columns for analysis
        """)
    
    # AI Configuration Section
    st.markdown("---")
    st.markdown("### 🤖 AI Assistant")
    use_ai = st.checkbox("Enable AI Question Parsing", value=False, 
                         help="Use Google Gemini to understand your questions")
    
    gemini_api_key = None
    if use_ai:
        with st.expander("⚙️ AI Settings", expanded=True):
            st.markdown("**Option 1:** Set environment variable `GEMINI_API_KEY`")
            st.markdown("**Option 2:** Enter API key below:")
            gemini_api_key = st.text_input(
                "Gemini API Key (optional)",
                type="password",
                help="Get free API key at https://makersuite.google.com/app/apikey"
            )
            st.caption("💡 Without AI, keyword matching will be used")
    
    # Store in session state
    st.session_state.use_ai = use_ai
    st.session_state.gemini_api_key = gemini_api_key

# Main content area
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Data Preview
    with st.expander("📊 Data Preview", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**First 5 rows:**")
            st.dataframe(df.head(), use_container_width=True)
        with col2:
            st.write("**Last 5 rows:**")
            st.dataframe(df.tail(), use_container_width=True)
    
    st.markdown("---")
    
    # Analysis Selection
    st.header("🔍 Select Analyses to Run")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_options = st.multiselect(
            "Choose one or more analyses:",
            [
                "📈 Exploratory Data Analysis (EDA)",
                "🔗 Correlation Analysis",
                "📉 Forecasting (Moving Avg & SES)",
                "📊 Stationarity Tests (ADF & KPSS)",
                "🎯 ARIMA Modeling",
                "📐 ACF & PACF Plots"
            ],
            default=["📈 Exploratory Data Analysis (EDA)"],
            help="Select multiple analyses to run them all at once"
        )
    
    with col2:
        # Item selection for item-specific analyses
        available_items = st.session_state.get('available_items', [])
        if available_items:
            selected_item = st.selectbox(
                "Select Column for Analysis:",
                available_items,
                help="For forecasting and ARIMA analyses"
            )
        else:
            selected_item = None
            st.warning("No numeric columns available")
    
    # Optional: Question input
    st.markdown("---")
    st.subheader("💬 Ask a Question (Optional)")
    user_question = st.text_area(
        "What would you like to know about your data?",
        placeholder="E.g., What is the trend in sales? Are sales and revenue correlated? Can you forecast next week's demand?",
        height=80
    )
    
    # AI Question Parsing
    if user_question and user_question.strip():
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🤖 Parse Question", help="Let AI suggest relevant analyses"):
                with st.spinner("Analyzing your question..."):
                    try:
                        available_items = st.session_state.get('available_items', [])
                        use_ai = st.session_state.get('use_ai', False)
                        api_key = st.session_state.get('gemini_api_key', None)
                        
                        insights = qh.get_ai_insights(
                            user_question, 
                            available_items,
                            use_ai=use_ai,
                            api_key=api_key
                        )
                        
                        st.session_state.ai_insights = insights
                        
                        # Display suggestions
                        st.success("✅ Question analyzed!")
                        
                        if insights.get('analyses'):
                            st.info(f"**Suggested Analyses:** {', '.join([a.split(' ', 1)[1] if ' ' in a else a for a in insights['analyses']])}")
                        
                        if insights.get('columns'):
                            st.info(f"**Relevant Columns:** {', '.join(insights['columns'])}")
                        
                        if insights.get('insights'):
                            for insight in insights['insights']:
                                st.write(f"💡 {insight}")
                        
                        # Auto-populate selections if available
                        if 'ai_insights' in st.session_state:
                            st.caption("👆 The suggestions above will be auto-selected when you run the analysis")
                            
                    except Exception as e:
                        st.error(f"Error parsing question: {str(e)}")
                        st.info("💡 Try enabling AI mode in the sidebar for better results")

    
    # Run Analysis Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    
    # Apply AI suggestions if available
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        insights = st.session_state.ai_insights
        
        # Auto-select suggested analyses
        if insights.get('analyses') and not analysis_options:
            analysis_options = insights['analyses']
        
        # Auto-select suggested column
        if insights.get('columns') and not selected_item:
            selected_item = insights['columns'][0] if insights['columns'] else selected_item
    
    # Execute analyses
    if run_button and analysis_options:
        st.session_state.analysis_results = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_analyses = len(analysis_options)
        
        for idx, analysis in enumerate(analysis_options):
            status_text.text(f"Running: {analysis}...")
            progress_bar.progress((idx + 1) / total_analyses)
            
            try:
                # EDA
                if "EDA" in analysis:
                    stats_df = ae.get_descriptive_stats(df)
                    st.session_state.analysis_results['eda'] = stats_df
                
                # Correlation
                if "Correlation" in analysis:
                    fig, corr_matrix = ae.create_correlation_heatmap(df)
                    st.session_state.analysis_results['correlation'] = {
                        'figure': fig,
                        'matrix': corr_matrix
                    }
                
                # Forecasting
                if "Forecasting" in analysis:
                    fig, metrics = ae.create_forecast_plot(df, item=selected_item)
                    st.session_state.analysis_results['forecasting'] = {
                        'figure': fig,
                        'metrics': metrics,
                        'item': selected_item
                    }
                
                # Stationarity Tests
                if "Stationarity" in analysis:
                    series = df[selected_item].values
                    adf_result = ae.perform_adf_test(series)
                    kpss_result = ae.perform_kpss_test(series)
                    st.session_state.analysis_results['stationarity'] = {
                        'adf': adf_result,
                        'kpss': kpss_result,
                        'item': selected_item
                    }
                
                # ARIMA
                if "ARIMA" in analysis:
                    fig, arima_result = ae.create_arima_plot(df, item=selected_item)
                    st.session_state.analysis_results['arima'] = {
                        'figure': fig,
                        'result': arima_result,
                        'item': selected_item
                    }
                
                # ACF & PACF
                if "ACF" in analysis or "PACF" in analysis:
                    series = df[selected_item].values
                    fig = ae.create_acf_pacf_plots(series)
                    st.session_state.analysis_results['acf_pacf'] = {
                        'figure': fig,
                        'item': selected_item
                    }
                    
            except Exception as e:
                st.error(f"Error in {analysis}: {str(e)}")
        
        progress_bar.empty()
        status_text.empty()
        st.success("✅ Analysis complete!")
    
    # Display Results
    if st.session_state.analysis_results:
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # EDA Results
        if 'eda' in st.session_state.analysis_results:
            st.subheader("📈 Descriptive Statistics")
            st.dataframe(st.session_state.analysis_results['eda'], use_container_width=True)
            st.markdown("---")
        
        # Correlation Results
        if 'correlation' in st.session_state.analysis_results:
            st.subheader("🔗 Correlation Analysis")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.pyplot(st.session_state.analysis_results['correlation']['figure'])
            with col2:
                st.write("**Correlation Matrix:**")
                st.dataframe(
                    st.session_state.analysis_results['correlation']['matrix'].style.background_gradient(cmap='coolwarm', axis=None),
                    use_container_width=True
                )
            st.markdown("---")
        
        # Forecasting Results
        if 'forecasting' in st.session_state.analysis_results:
            st.subheader(f"📉 Forecasting Analysis - {st.session_state.analysis_results['forecasting']['item']}")
            st.pyplot(st.session_state.analysis_results['forecasting']['figure'])
            
            col1, col2 = st.columns(2)
            metrics = st.session_state.analysis_results['forecasting']['metrics']
            with col1:
                st.metric("Moving Average RMSE", f"{metrics['MA']['RMSE']:.2f}")
                st.metric("Moving Average MAPE", f"{metrics['MA']['MAPE']:.2f}%")
            with col2:
                st.metric("SES RMSE", f"{metrics['SES']['RMSE']:.2f}")
                st.metric("SES MAPE", f"{metrics['SES']['MAPE']:.2f}%")
            st.markdown("---")
        
        # Stationarity Results
        if 'stationarity' in st.session_state.analysis_results:
            st.subheader(f"📊 Stationarity Tests - {st.session_state.analysis_results['stationarity']['item']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Augmented Dickey-Fuller Test**")
                adf = st.session_state.analysis_results['stationarity']['adf']
                st.metric("ADF Statistic", f"{adf['statistic']:.4f}")
                st.metric("p-value", f"{adf['p_value']:.4f}")
                if adf['is_stationary']:
                    st.success("✅ Series is STATIONARY (p < 0.05)")
                else:
                    st.warning("⚠️ Series is NON-STATIONARY (p ≥ 0.05)")
            
            with col2:
                st.write("**KPSS Test**")
                kpss = st.session_state.analysis_results['stationarity']['kpss']
                st.metric("KPSS Statistic", f"{kpss['statistic']:.4f}")
                st.metric("p-value", f"{kpss['p_value']:.4f}")
                if kpss['is_stationary']:
                    st.success("✅ Series is STATIONARY (p > 0.05)")
                else:
                    st.warning("⚠️ Series is NON-STATIONARY (p ≤ 0.05)")
            st.markdown("---")
        
        # ACF & PACF Results
        if 'acf_pacf' in st.session_state.analysis_results:
            st.subheader(f"📐 ACF & PACF Plots - {st.session_state.analysis_results['acf_pacf']['item']}")
            st.pyplot(st.session_state.analysis_results['acf_pacf']['figure'])
            st.markdown("---")
        
        # ARIMA Results
        if 'arima' in st.session_state.analysis_results:
            st.subheader(f"🎯 ARIMA Modeling - {st.session_state.analysis_results['arima']['item']}")
            st.pyplot(st.session_state.analysis_results['arima']['figure'])
            
            col1, col2 = st.columns(2)
            result = st.session_state.analysis_results['arima']['result']
            with col1:
                st.metric("ARIMA RMSE", f"{result['rmse']:.2f}")
            with col2:
                st.metric("ARIMA MAPE", f"{result['mape']:.2f}%")
            
            with st.expander("View ARIMA Model Summary"):
                st.text(str(result['summary']))
            st.markdown("---")
        
        # User Question Response (if provided)
        if user_question:
            st.subheader("💬 Your Question")
            st.info(user_question)
            st.write("**AI Response:** The analyses above provide insights into your question. Review the relevant sections for detailed answers.")

else:
    # No data loaded - show instructions
    st.info("👆 Please upload an Excel file from the sidebar to get started!")
    
    st.markdown("### 🚀 Quick Start Guide")
    st.markdown("""
    1. **Upload your Excel file** using the sidebar (or click "Use Sample Data")
    2. **Select analyses** you want to run using the multiselect dropdown
    3. **Choose a column** from your dataset for item-specific analyses
    4. **Optionally ask a question** about your data
    5. **Click "Run Analysis"** to see results instantly
    
    #### 📋 Available Analyses:
    - **EDA**: Descriptive statistics (mean, median, std dev, CV)
    - **Correlation**: Heatmap showing relationships between variables
    - **Forecasting**: 7-day Moving Average & Simple Exponential Smoothing
    - **Stationarity**: ADF and KPSS statistical tests
    - **ARIMA**: ARIMA(2,1,1) modeling with train-test split
    - **ACF & PACF**: Autocorrelation plots for time series analysis
    
    #### 💡 Your Data Should Have:
    - A **Date** column (required)
    - One or more **numeric columns** to analyze
    - Data sorted or sortable by date
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Example Data Format")
    sample_df = pd.DataFrame({
        'Date': ['2012-10-01', '2012-10-02', '2012-10-03'],
        'Sales': [120, 135, 142],
        'Revenue': [9500, 11000, 10500],
        'Customers': [85, 92, 88]
    })
    st.dataframe(sample_df, use_container_width=True)
    st.caption("Your data can have any column names - the dashboard will automatically detect and use your numeric columns!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>Built with Streamlit | SCA Dashboard</div>",
    unsafe_allow_html=True
)
