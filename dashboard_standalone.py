#!/usr/bin/env python3
"""
YVote Dashboard - Standalone Version
====================================

A simplified version that can run independently and show data
even when the tracker is not running. This version reads existing
CSV data and provides historical analysis.

Usage:
    streamlit run dashboard_standalone.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json

# Page config
st.set_page_config(
    page_title="YVote Monitor - Standalone",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title { 
        font-size: 2.5rem; 
        text-align: center; 
        color: #1f77b4; 
        margin-bottom: 2rem; 
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    """Load voting data from CSV file"""
    csv_path = Path("yvote_v3_log.csv")
    
    if not csv_path.exists():
        return None
    
    try:
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    """Main dashboard function"""
    st.markdown('<div class="main-title">📊 YVote Data Analyzer</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df is None:
        st.error("""
        🚫 **No Data Found**
        
        This dashboard requires the CSV file `yvote_v3_log.csv` to exist.
        
        To get data:
        1. Run the tracker: `python track_yvote_v3_1.py`
        2. Wait for it to collect at least one data point
        3. Refresh this page
        """)
        return
    
    if df.empty:
        st.warning("CSV file exists but contains no data.")
        return
    
    # Sidebar controls
    st.sidebar.title("📊 Data Controls")
    
    # Time range filter
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        # Filter dataframe
        mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        filtered_df = df.loc[mask]
    else:
        filtered_df = df
    
    # Candidate filter
    all_candidates = sorted(df['name'].unique())
    selected_candidates = st.sidebar.multiselect(
        "Select Candidates",
        options=all_candidates,
        default=all_candidates  # Show all candidates by default
    )
    
    if selected_candidates:
        filtered_df = filtered_df[filtered_df['name'].isin(selected_candidates)]
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Data info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📈 Data Summary**")
    st.sidebar.write(f"Total Records: {len(df):,}")
    st.sidebar.write(f"Candidates: {df['name'].nunique()}")
    st.sidebar.write(f"Time Span: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
    
    # Main content
    if filtered_df.empty:
        st.warning("No data matches your current filters.")
        return
    
    # Key metrics
    latest_data = filtered_df.loc[filtered_df['timestamp'] == filtered_df['timestamp'].max()]
    total_votes = latest_data['votes'].sum() if not latest_data.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🗳️ Total Votes", f"{total_votes:,}")
    
    with col2:
        st.metric("👥 Candidates", len(selected_candidates))
    
    with col3:
        latest_time = filtered_df['timestamp'].max()
        time_ago = datetime.now() - latest_time
        hours_ago = int(time_ago.total_seconds() / 3600)
        st.metric("⏰ Latest Data", f"{hours_ago}h ago")
    
    with col4:
        # Calculate data frequency
        time_diffs = filtered_df.groupby('timestamp').size().index.to_series().diff().dropna()
        avg_interval = time_diffs.mean().total_seconds() / 60 if len(time_diffs) > 0 else 0
        st.metric("📊 Avg Interval", f"{avg_interval:.1f}min")
    
    # Charts
    tab1, tab2, tab3 = st.tabs(["📈 Vote Trends", "📊 Rankings", "📋 Data Table"])
    
    with tab1:
        st.subheader("Vote Progression Over Time")
        
        if not filtered_df.empty:
            fig = px.line(
                filtered_df,
                x='timestamp',
                y='votes',
                color='name',
                title='Vote Count Progression',
                labels={'votes': 'Votes', 'timestamp': 'Time'}
            )
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # Percentage chart
            st.subheader("Percentage Share Over Time")
            fig2 = px.line(
                filtered_df,
                x='timestamp',
                y='percent',
                color='name',
                title='Percentage Share Trends',
                labels={'percent': 'Percentage (%)', 'timestamp': 'Time'}
            )
            fig2.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.subheader("Current Rankings")
        
        if not latest_data.empty:
            ranking_df = latest_data.sort_values('rank')[['rank', 'name', 'votes', 'percent']]
            
            # Create a bar chart
            fig = px.bar(
                ranking_df,
                x='name',
                y='votes',
                title='Current Vote Distribution',
                labels={'votes': 'Votes', 'name': 'Candidate'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Rankings table
            st.dataframe(
                ranking_df.style.format({
                    'votes': '{:,}',
                    'percent': '{:.2f}%'
                }),
                use_container_width=True
            )
    
    with tab3:
        st.subheader("Raw Data")
        
        # Display options
        col1, col2 = st.columns(2)
        with col1:
            show_latest_only = st.checkbox("Show only latest data")
        with col2:
            records_limit = st.selectbox("Records to show", [50, 100, 500, 1000, "All"])
        
        display_df = filtered_df.copy()
        
        if show_latest_only:
            latest_timestamp = display_df['timestamp'].max()
            display_df = display_df[display_df['timestamp'] == latest_timestamp]
        
        if records_limit != "All":
            display_df = display_df.tail(records_limit)
        
        # Format the dataframe for display
        display_df = display_df.sort_values(['timestamp', 'rank'], ascending=[False, True])
        
        st.dataframe(
            display_df.style.format({
                'votes': '{:,}',
                'percent': '{:.6f}%',
                'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
            }),
            use_container_width=True
        )
        
        # Download button
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv_data,
            file_name=f"yvote_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()