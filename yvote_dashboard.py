#!/usr/bin/env python3
"""
YVote Real-Time Monitoring Dashboard
====================================

A Streamlit-based dashboard for monitoring YVote tracking data in real-time.
Displays live voting statistics, candidate rankings, and trend analysis.

Requirements:
- streamlit
- plotly
- pandas
- altair

Usage:
    streamlit run yvote_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="YVote Live Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLING ===
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .candidate-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# === DATA LOADING FUNCTIONS ===
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_voting_data():
    """Load and process voting data from CSV"""
    csv_path = Path("yvote_v3_log.csv")
    
    if not csv_path.exists():
        return pd.DataFrame(), {}
    
    try:
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get latest state
        state_path = Path("state_v3.json")
        state = {}
        if state_path.exists():
            with open(state_path, 'r') as f:
                state = json.load(f)
        
        return df, state
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), {}

def get_latest_data(df):
    """Get the most recent voting data"""
    if df.empty:
        return pd.DataFrame()
    
    latest_time = df['timestamp'].max()
    return df[df['timestamp'] == latest_time].sort_values('rank')

def calculate_trends(df, hours=24):
    """Calculate voting trends over the specified time period"""
    if df.empty:
        return pd.DataFrame()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_df = df[df['timestamp'] >= cutoff_time]
    
    if recent_df.empty:
        return pd.DataFrame()
    
    # Calculate trends for each candidate
    trends = []
    for name in recent_df['name'].unique():
        candidate_data = recent_df[recent_df['name'] == name].sort_values('timestamp')
        if len(candidate_data) >= 2:
            first_votes = candidate_data.iloc[0]['votes']
            last_votes = candidate_data.iloc[-1]['votes']
            vote_change = last_votes - first_votes
            
            first_percent = candidate_data.iloc[0]['percent']
            last_percent = candidate_data.iloc[-1]['percent']
            percent_change = last_percent - first_percent
            
            trends.append({
                'name': name,
                'vote_change': vote_change,
                'percent_change': percent_change,
                'current_votes': last_votes,
                'current_percent': last_percent,
                'current_rank': candidate_data.iloc[-1]['rank']
            })
    
    return pd.DataFrame(trends)

def check_tracker_status():
    """Check if the tracker is currently running"""
    state_path = Path("state_v3.json")
    if not state_path.exists():
        return False, "No state file found"
    
    try:
        # Check if state file was modified recently (within 10 minutes)
        last_modified = datetime.fromtimestamp(state_path.stat().st_mtime)
        time_diff = datetime.now() - last_modified
        
        if time_diff.total_seconds() < 600:  # 10 minutes
            return True, f"Running (last update: {time_diff.total_seconds():.0f}s ago)"
        else:
            return False, f"Stopped (last update: {time_diff.total_seconds()//60:.0f}min ago)"
    except:
        return False, "Unable to determine status"

# === DASHBOARD COMPONENTS ===
def render_header():
    """Render the main header and status"""
    st.markdown('<div class="main-header">🗳️ YVote Live Monitor</div>', unsafe_allow_html=True)
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        is_running, status_msg = check_tracker_status()
        status_class = "status-running" if is_running else "status-stopped"
        status_icon = "🟢" if is_running else "🔴"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem;">
            <span class="{status_class}">{status_icon} Tracker Status: {status_msg}</span>
        </div>
        """, unsafe_allow_html=True)

def render_key_metrics(df, state):
    """Render key voting metrics"""
    if df.empty:
        st.warning("No data available. Make sure the tracker is running and has collected data.")
        return
    
    latest_data = get_latest_data(df)
    current_total = state.get('current_total', 0)
    
    # Calculate some basic statistics
    total_candidates = len(latest_data) if not latest_data.empty else 0
    last_update = df['timestamp'].max() if not df.empty else None
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🗳️ Total Votes",
            value=f"{current_total:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="👥 Candidates",
            value=total_candidates,
            delta=None
        )
    
    with col3:
        if last_update:
            time_since = datetime.now() - last_update
            minutes_ago = int(time_since.total_seconds() / 60)
            st.metric(
                label="⏱️ Last Update",
                value=f"{minutes_ago}m ago",
                delta=None
            )
        else:
            st.metric(
                label="⏱️ Last Update",
                value="Never",
                delta=None
            )
    
    with col4:
        if not df.empty:
            # Calculate votes per minute based on recent data
            recent_hours = 2
            recent_data = df[df['timestamp'] >= datetime.now() - timedelta(hours=recent_hours)]
            if len(recent_data) > 1:
                time_span = (recent_data['timestamp'].max() - recent_data['timestamp'].min()).total_seconds() / 60
                total_votes_change = recent_data.groupby('timestamp')['votes'].sum().max() - recent_data.groupby('timestamp')['votes'].sum().min()
                votes_per_min = total_votes_change / time_span if time_span > 0 else 0
                st.metric(
                    label="📈 Votes/min",
                    value=f"{votes_per_min:.1f}",
                    delta=None
                )
            else:
                st.metric(
                    label="📈 Votes/min",
                    value="N/A",
                    delta=None
                )

def render_current_rankings(df):
    """Render current candidate rankings"""
    if df.empty:
        return
    
    st.subheader("🏆 Current Rankings")
    
    latest_data = get_latest_data(df)
    if latest_data.empty:
        st.warning("No current ranking data available.")
        return
    
    # Create a nice ranking display
    for _, candidate in latest_data.iterrows():
        rank = candidate['rank']
        name = candidate['name']
        votes = candidate['votes']
        percent = candidate['percent']
        
        # Determine medal emoji
        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"
        else:
            medal = f"#{rank}"
        
        # Create progress bar based on percentage
        progress = min(percent / 100, 1.0) if percent > 0 else 0
        
        st.markdown(f"""
        <div class="candidate-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 1rem;">{medal}</span>
                    <strong style="font-size: 1.2rem;">{name}</strong>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.1rem; font-weight: bold;">{votes:,} votes</div>
                    <div style="color: #666;">{percent:.2f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_voting_trends(df):
    """Render voting trend charts"""
    if df.empty:
        return
    
    st.subheader("📊 Voting Trends")
    
    # Time range selector
    col1, col2 = st.columns([3, 1])
    with col2:
        time_range = st.selectbox(
            "Time Range",
            options=[6, 12, 24, 48, 72],
            index=2,
            format_func=lambda x: f"Last {x} hours"
        )
    
    # Filter data based on time range
    cutoff_time = datetime.now() - timedelta(hours=time_range)
    filtered_df = df[df['timestamp'] >= cutoff_time]
    
    if filtered_df.empty:
        st.warning(f"No data available for the last {time_range} hours.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Vote Progression", "📊 Percentage Trends", "🔄 Total Votes"])
    
    with tab1:
        # Vote progression chart
        fig = px.line(
            filtered_df,
            x='timestamp',
            y='votes',
            color='name',
            title='Vote Count Progression',
            labels={'votes': 'Votes', 'timestamp': 'Time'},
            line_shape='linear'
        )
        fig.update_layout(
            height=500,
            hovermode='x unified',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Percentage trends
        fig = px.line(
            filtered_df,
            x='timestamp',
            y='percent',
            color='name',
            title='Percentage Share Trends',
            labels={'percent': 'Percentage (%)', 'timestamp': 'Time'},
            line_shape='linear'
        )
        fig.update_layout(
            height=500,
            hovermode='x unified',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Total votes over time
        total_votes_df = filtered_df.groupby('timestamp')['votes'].sum().reset_index()
        fig = px.line(
            total_votes_df,
            x='timestamp',
            y='votes',
            title='Total Votes Over Time',
            labels={'votes': 'Total Votes', 'timestamp': 'Time'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_trend_analysis(df):
    """Render trend analysis and insights"""
    if df.empty:
        return
    
    st.subheader("🔍 Trend Analysis")
    
    # Calculate trends for different time periods
    periods = [1, 6, 24]
    
    for hours in periods:
        with st.expander(f"📅 Last {hours} hour{'s' if hours > 1 else ''} Analysis"):
            trends_df = calculate_trends(df, hours)
            
            if trends_df.empty:
                st.info(f"Not enough data for {hours} hour analysis.")
                continue
            
            # Sort by vote change
            trends_df = trends_df.sort_values('vote_change', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top Gainers (Votes)**")
                for _, row in trends_df.head(3).iterrows():
                    change = row['vote_change']
                    if change > 0:
                        st.write(f"🔥 **{row['name']}**: +{change:,} votes")
                    elif change == 0:
                        st.write(f"➡️ **{row['name']}**: No change")
                    else:
                        st.write(f"📉 **{row['name']}**: {change:,} votes")
            
            with col2:
                st.write("**Percentage Changes**")
                for _, row in trends_df.head(3).iterrows():
                    change = row['percent_change']
                    if change > 0:
                        st.write(f"📈 **{row['name']}**: +{change:.3f}%")
                    elif change == 0:
                        st.write(f"➡️ **{row['name']}**: No change")
                    else:
                        st.write(f"📉 **{row['name']}**: {change:.3f}%")

def render_sidebar():
    """Render sidebar with controls and information"""
    st.sidebar.title("⚙️ Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=True)
    
    if auto_refresh:
        refresh_interval = st.sidebar.selectbox(
            "Refresh Interval",
            options=[30, 60, 120, 300],
            index=0,
            format_func=lambda x: f"{x} seconds"
        )
        st.sidebar.info(f"Auto-refreshing every {refresh_interval} seconds")
    
    st.sidebar.divider()
    
    # Data information
    st.sidebar.subheader("📊 Data Information")
    
    # Check data files
    csv_exists = Path("yvote_v3_log.csv").exists()
    state_exists = Path("state_v3.json").exists()
    
    st.sidebar.write(f"CSV File: {'✅' if csv_exists else '❌'}")
    st.sidebar.write(f"State File: {'✅' if state_exists else '❌'}")
    
    if csv_exists:
        try:
            df_info = pd.read_csv("yvote_v3_log.csv")
            st.sidebar.write(f"Records: {len(df_info):,}")
            if not df_info.empty:
                st.sidebar.write(f"Date Range: {df_info['timestamp'].min()[:10]} to {df_info['timestamp'].max()[:10]}")
        except:
            st.sidebar.write("Unable to read CSV")
    
    st.sidebar.divider()
    
    # Manual actions
    st.sidebar.subheader("🛠️ Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Download buttons
    if csv_exists:
        with open("yvote_v3_log.csv", "rb") as file:
            st.sidebar.download_button(
                label="📥 Download CSV",
                data=file,
                file_name=f"yvote_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    st.sidebar.divider()
    
    # Help information
    with st.sidebar.expander("ℹ️ Help"):
        st.write("""
        **Dashboard Features:**
        - Real-time vote monitoring
        - Candidate rankings
        - Trend analysis
        - Historical data visualization
        
        **Requirements:**
        - YVote tracker must be running
        - Data files: yvote_v3_log.csv, state_v3.json
        
        **Troubleshooting:**
        - If no data appears, check tracker status
        - Use manual refresh if auto-refresh fails
        - Check file permissions if downloads fail
        """)
    
    return auto_refresh, refresh_interval if 'auto_refresh' in locals() and auto_refresh else 30

# === MAIN DASHBOARD ===
def main():
    """Main dashboard function"""
    # Render sidebar and get settings
    auto_refresh, refresh_interval = render_sidebar()
    
    # Render header
    render_header()
    
    # Load data
    df, state = load_voting_data()
    
    # Main content
    if df.empty:
        st.error("""
        🚫 **No Data Available**
        
        The dashboard couldn't find any voting data. Please ensure:
        1. The YVote tracker is running (`python track_yvote_v3_1.py`)
        2. The tracker has collected at least one data point
        3. The CSV file `yvote_v3_log.csv` exists in the current directory
        
        Once the tracker is running and has collected data, refresh this page.
        """)
        return
    
    # Render dashboard components
    render_key_metrics(df, state)
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_current_rankings(df)
    
    with col2:
        render_trend_analysis(df)
    
    st.divider()
    render_voting_trends(df)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

# === RUN DASHBOARD ===
if __name__ == "__main__":
    main()